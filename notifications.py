import os
import requests
import logging
from dotenv import load_dotenv

load_dotenv()

class NotificationManager:
    def __init__(self, config: dict):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Telegram ayarları (.env dosyasından çekilir)
        self.bot_token = os.getenv("TELEGRAM_BOT_TOKEN", "BURAYA_TOKEN_YAZIN")
        self.chat_id = os.getenv("TELEGRAM_CHAT_ID", "BURAYA_CHAT_ID_YAZIN")
        self.telegram_url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"

    def _send_telegram(self, text: str):
        if self.chat_id == "BURAYA_CHAT_ID_YAZIN":
            return  # Chat ID ayarlanmamışsa gönderme
            
        try:
            payload = {
                "chat_id": self.chat_id,
                "text": text,
                "parse_mode": "HTML"
            }
            response = requests.post(self.telegram_url, data=payload, timeout=5)
            if response.status_code != 200:
                self.logger.error(f"Telegram'a gönderilemedi! Hata kodu: {response.status_code}, Detay: {response.text}")
            else:
                self.logger.info("✅ Telegram bildirimi başarıyla gönderildi.")
        except Exception as e:
            self.logger.error(f"Telegram bildirim hatası: {e}")

    def notify_rate_limit(self, reason: str):
        self._send_telegram(f"⚠️ <b>Hız Sınırı (Rate Limit)</b>\nSınır aşıldı: {reason}")

    def notify_success(self, phone: str):
        pass # Her mesajda bildirim atmak spam yapabilir, bu yüzden bunu boş bırakıyoruz

    def notify_failure(self, phone: str, reason: str):
        self._send_telegram(f"❌ <b>Gönderim Hatası</b>\nNumara: {phone}\nSebep: {reason}")

    def notify_stats(self, success_count: int, failed_count: int):
        self._send_telegram(f"✅ <b>Görev Tamamlandı</b>\nBaşarılı: {success_count}\nBaşarısız: {failed_count}")

