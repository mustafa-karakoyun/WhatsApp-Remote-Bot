"""
WhatsApp Bot - Ana Modül
Gelişmiş WhatsApp otomasyon botu - Tüm özellikler dahil
"""

import os
import sys
import time
import random
import logging
from datetime import datetime
from typing import Optional, List, Dict
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager

from dotenv import load_dotenv

from utils import (
    load_config, load_templates, render_template, 
    parse_recipients, MessageStats,
    random_delay, ensure_directory
)
from rate_limiter import RateLimiter, MessageQueue
from notifications import NotificationManager
from reporting import ReportGenerator


class WhatsAppBot:
    """Gelişmiş WhatsApp Bot Sınıfı"""
    
    def __init__(self, config_path: str = "config.yaml"):
        """Bot'u başlat"""
        # Konfigürasyonu yükle
        self.config = load_config(config_path)
        
        # Logging ayarla
        self._setup_logging()
        
        # Bileşenleri başlat
        self.rate_limiter = RateLimiter(
            max_per_hour=self.config['security']['rate_limiting']['max_messages_per_hour'],
            max_per_day=self.config['security']['rate_limiting']['max_messages_per_day'],
            cooldown_seconds=self.config['security']['rate_limiting']['cooldown_after_limit']
        )
        self.message_queue = MessageQueue(self.rate_limiter)
        self.notifier = NotificationManager(self.config)
        self.reporter = ReportGenerator(self.config['reporting']['output_directory'])
        self.stats = MessageStats()
        
        # Şablonları yükle
        try:
            self.templates = load_templates()
        except Exception as e:
            self.logger.warning(f"Şablonlar yüklenemedi: {e}")
            self.templates = {'templates': {}}
        
        # Driver başlatma için değişkenler
        self.driver = None
        self.wait = None
        
        # Session kontrolü
        self.session_valid = False
        
        self.logger.info("WhatsApp Bot başlatıldı")
    
    def _setup_logging(self):
        """Logging sistemini kur"""
        log_config = self.config['logging']
        
        # Logger oluştur
        self.logger = logging.getLogger('WhatsAppBot')
        self.logger.setLevel(getattr(logging, log_config['level']))
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Console handler
        if log_config['console_enabled']:
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)
        
        # File handler
        if log_config['file_enabled']:
            ensure_directory(os.path.dirname(log_config['file_path']))
            from logging.handlers import RotatingFileHandler
            file_handler = RotatingFileHandler(
                log_config['file_path'],
                maxBytes=log_config['file_max_bytes'],
                backupCount=log_config['file_backup_count']
            )
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)
    
    def _init_driver(self):
        """WebDriver'ı başlat"""
        try:
            browser_config = self.config['browser']
            
            chrome_options = Options()
            
            # Profil dizini
            profile_path = os.path.abspath(browser_config['profile_path'])
            ensure_directory(profile_path)
            chrome_options.add_argument(f"user-data-dir={profile_path}")
            
            # Headless mode
            if browser_config['headless']:
                chrome_options.add_argument("--headless=new")
            
            # Temel ayarlar
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument(f"--window-size={browser_config['window_size']}")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            
            # User agent rotation
            if 'user_agents' in browser_config:
                user_agent = random.choice(browser_config['user_agents'])
                chrome_options.add_argument(f"user-agent={user_agent}")
            
            # Anti-detection
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            # WebDriver başlat
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            
            # Anti-detection script
            self.driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
                'source': '''
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => undefined
                    })
                '''
            })
            
            # Wait objesi
            self.wait = WebDriverWait(
                self.driver, 
                self.config['messaging']['timeouts']['element_wait']
            )
            
            self.logger.info("WebDriver başarıyla başlatıldı")
            return True
            
        except Exception as e:
            self.logger.error(f"WebDriver başlatma hatası: {e}")
            return False
    
    def _check_session(self) -> bool:
        """WhatsApp oturumunun açık olup olmadığını kontrol et"""
        try:
            # WhatsApp Web'e git
            self.driver.get("https://web.whatsapp.com")
            time.sleep(5)
            
            # QR kod var mı kontrol et
            try:
                qr_code = self.driver.find_element(By.XPATH, '//canvas[@aria-label="Scan me!"]')
                self.logger.warning("⚠️  QR kod bulundu - oturum açmanız gerekiyor")
                print("\n" + "="*60)
                print("⚠️  WhatsApp Web QR kodunu taramanız gerekiyor!")
                print("📱 Telefonunuzda WhatsApp'ı açın")
                print("👉 Ayarlar > Bağlı Cihazlar > Cihaz Bağla")
                print("📷 QR kodu tarayın")
                print("="*60 + "\n")
                
                # QR kod taranana kadar bekle
                qr_timeout = self.config['messaging']['timeouts']['qr_scan']
                self.logger.info(f"QR kod taraması için {qr_timeout} saniye bekleniyor...")
                
                for remaining in range(qr_timeout, 0, -5):
                    print(f"⏳ Kalan süre: {remaining} saniye...", end='\r')
                    time.sleep(5)
                    
                    # QR kod kayboldu mu?
                    try:
                        self.driver.find_element(By.XPATH, '//canvas[@aria-label="Scan me!"]')
                    except NoSuchElementException:
                        self.logger.info("✅ QR kod tarandı!")
                        print("\n✅ Oturum başarıyla açıldı!")
                        self.session_valid = True
                        return True
                
                self.logger.error("❌ QR kod zaman aşımı")
                return False
                
            except NoSuchElementException:
                # QR kod yok - oturum açık
                self.logger.info("✅ WhatsApp oturumu açık")
                self.session_valid = True
                return True
                
        except Exception as e:
            self.logger.error(f"Oturum kontrolü hatası: {e}")
            return False
    
    def _human_type(self, element, text: str):
        """İnsan gibi yazma simülasyonu"""
        if not self.config['security']['human_simulation']['enabled']:
            element.send_keys(text)
            return
        
        min_delay = self.config['security']['human_simulation']['typing_delay_min']
        max_delay = self.config['security']['human_simulation']['typing_delay_max']
        
        for char in text:
            element.send_keys(char)
            time.sleep(random_delay(min_delay, max_delay))
    
    def send_message(self, phone: str, message: str) -> bool:
        """
        Mesaj gönder
        
        Args:
            phone: Alıcı telefon numarası (+905551234567)
            message: Gönderilecek mesaj
        
        Returns:
            bool: Başarılı ise True
        """
        try:
            # Rate limit kontrolü
            can_send, reason = self.rate_limiter.can_send()
            if not can_send:
                self.logger.warning(f"Rate limit: {reason}")
                self.notifier.notify_rate_limit(reason)
                return False
            
            # URL oluştur
            url = f"https://web.whatsapp.com/send?phone={phone}"
            self.driver.get(url)
            
            self.logger.info(f"Sohbet açılıyor: {phone}")
            
            # Mesaj kutusu bekle
            message_box_xpath = '//div[@contenteditable="true"][@data-tab="10"]'
            
            try:
                message_box = self.wait.until(
                    EC.presence_of_element_located((By.XPATH, message_box_xpath))
                )
            except TimeoutException:
                # Alternatif selector dene
                message_box_xpath = '//div[@contenteditable="true"][@role="textbox"]'
                message_box = self.wait.until(
                    EC.presence_of_element_located((By.XPATH, message_box_xpath))
                )
            
            message_box.click()
            time.sleep(1)
            

            # Mesajı yaz
            self.logger.info("Mesaj yazılıyor...")
            for line in message.split('\n'):
                self._human_type(message_box, line)
                if line != message.split('\n')[-1]:  # Son satır değilse
                    message_box.send_keys(Keys.SHIFT, Keys.ENTER)
            
            # İnsan davranışı - gönder öncesi bekle
            if self.config['security']['human_simulation']['enabled']:
                delay = random_delay(
                    self.config['security']['human_simulation']['message_delay_min'],
                    self.config['security']['human_simulation']['message_delay_max']
                )
                time.sleep(delay)
            
            # Gönder
            message_box.send_keys(Keys.ENTER)
            self.logger.info("✅ Mesaj gönderildi")
            
            # İstatistik güncelle
            self.stats.add_success(phone)
            self.rate_limiter.record_message()
            
            # Mesajın gitmesi için bekle
            time.sleep(3)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Mesaj gönderme hatası: {e}")
            self.stats.add_failure(phone)
            return False
    
    def send_template_message(self, phone: str, template_name: str, 
                            variables: Dict[str, str] = None) -> bool:
        """Şablon mesaj gönder"""
        try:
            if variables is None:
                variables = {}
            
            # Şablonu render et
            from utils import render_template
            message = render_template(template_name, variables, self.templates)
            
            return self.send_message(phone, message)
            
        except Exception as e:
            self.logger.error(f"Şablon mesaj hatası: {e}")
            return False
    
    def send_bulk_messages(self, recipients: List[str], message: str, 
                          delay_between: tuple = (5, 10)) -> Dict[str, int]:
        """
        Toplu mesaj gönder
        
        Args:
            recipients: Alıcı listesi
            message: Mesaj metni
            delay_between: Mesajlar arası gecikme (min, max) saniye
        
        Returns:
            Dict: {'success': count, 'failed': count}
        """
        results = {'success': 0, 'failed': 0}
        
        for i, recipient in enumerate(recipients, 1):
            self.logger.info(f"📤 Mesaj gönderiliyor ({i}/{len(recipients)}): {recipient}")
            
            success = self.send_message(recipient, message)
            
            if success:
                results['success'] += 1
                self.notifier.notify_success(recipient)
            else:
                results['failed'] += 1
                self.notifier.notify_failure(recipient, "Gönderim başarısız")
            
            # Son mesaj değilse bekle
            if i < len(recipients):
                wait_time = random_delay(*delay_between)
                self.logger.info(f"⏳ Sonraki mesaj için {wait_time:.1f} saniye bekleniyor...")
                time.sleep(wait_time)
        
        return results
    
    def close(self):
        """Bot'u kapat ve temizlik yap"""
        if self.driver:
            self.driver.quit()
            self.logger.info("WebDriver kapatıldı")
        
        # Rapor oluştur
        if self.config['reporting']['enabled']:
            self.logger.info("📊 Rapor oluşturuluyor...")
            report_files = self.reporter.generate_report(
                self.stats,
                formats=self.config['reporting']['formats']
            )
            
            # Özet göster
            print(self.reporter.generate_summary(self.stats))
            
            # Bildirim gönder
            if self.config['reporting']['include_statistics']:
                self.notifier.notify_stats(self.stats.to_dict())
    
    def __enter__(self):
        """Context manager desteği"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager çıkış"""
        self.close()


def main():
    """Ana fonksiyon"""
    # .env yükle
    load_dotenv()
    
    # Bot başlat
    with WhatsAppBot() as bot:
        # WebDriver başlat
        if not bot._init_driver():
            bot.logger.error("WebDriver başlatılamadı!")
            return
        
        # Oturum kontrolü
        if not bot._check_session():
            bot.logger.error("WhatsApp oturumu açılamadı!")
            return
        
        # Alıcıları al
        recipients_str = os.getenv('RECIPIENTS', '+905467937512')
        recipients = parse_recipients(recipients_str)
        
        if not recipients:
            bot.logger.error("Geçerli alıcı bulunamadı!")
            return
        
        # Mesajı al
        message = os.getenv('DEFAULT_MESSAGE', 'Merhaba! Bu otomatik bir mesajdır.')
        
        # Mesajları gönder
        bot.logger.info(f"📨 {len(recipients)} alıcıya mesaj gönderilecek")
        results = bot.send_bulk_messages(recipients, message)
        
        bot.logger.info(f"✅ Başarılı: {results['success']} | ❌ Başarısız: {results['failed']}")
        bot.notifier.notify_stats(results['success'], results['failed'])


if __name__ == "__main__":
    main()