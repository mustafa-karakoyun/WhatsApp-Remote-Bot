import telebot
import os
import threading
from dotenv import load_dotenv
from botV2 import WhatsAppBot

# Ortam değişkenlerini yükle
load_dotenv()

# Telegram Ayarları (.env dosyasından çekilir)
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "BURAYA_TOKEN_GELECEK")
AUTHORIZED_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "BURAYA_CHAT_ID_GELECEK")

bot = telebot.TeleBot(BOT_TOKEN)

def send_whatsapp_message(chat_id, phone, text):
    """WhatsApp botunu arka planda çalıştırır ve mesajı atar"""
    bot.send_message(chat_id, f"🔄 WhatsApp başlatılıyor...\n\nHedef: {phone}\nMesaj: {text}")
    
    try:
        wp_bot = WhatsAppBot()
        if not wp_bot._init_driver():
            bot.send_message(chat_id, "❌ Hata: Tarayıcı başlatılamadı.")
            return
            
        if not wp_bot._check_session():
            wp_bot.close()
            bot.send_message(chat_id, "❌ Hata: WhatsApp oturumu kapalı! Lütfen sunucudan QR kod okutun.")
            return

        # Numaraları ayır (virgülle yazılmışsa liste yapar, tekse tek numaralık liste olur)
        phones = [p.strip() for p in phone.split(',') if p.strip()]
        
        # Mesajları toplu gönder
        results = wp_bot.send_bulk_messages(phones, text)
        wp_bot.close()
        
        bot.send_message(chat_id, f"✅ İşlem Tamamlandı!\nBaşarılı Gönderim: {results['success']}\nBaşarısız Gönderim: {results['failed']}")
            
    except Exception as e:
        bot.send_message(chat_id, f"❌ Kritik bir hata oluştu: {str(e)}")


@bot.message_handler(commands=['start', 'yardim'])
def send_welcome(message):
    if str(message.chat.id) != AUTHORIZED_CHAT_ID:
        bot.reply_to(message, "⛔ Bu botu kullanmaya yetkiniz yok.")
        return
        
    welcome_text = (
        "🤖 **WhatsApp Uzaktan Kontrol Botuna Hoş Geldiniz!**\n\n"
        "Mesaj göndermek için şu komutu kullanın:\n"
        "`/gonder +905551234567 Merhaba, nasılsın?`\n\n"
        "Lütfen numarayı boşluksuz ve +90 (veya ülke kodu) ile başlatarak yazın."
    )
    bot.reply_to(message, welcome_text, parse_mode='Markdown')


@bot.message_handler(commands=['gonder'])
def handle_gonder(message):
    if str(message.chat.id) != AUTHORIZED_CHAT_ID:
        bot.reply_to(message, "⛔ Bu botu kullanmaya yetkiniz yok.")
        return

    # Komutu parçala
    try:
        # Virgüllerden sonraki boşlukları sil ki numaralar tek bir kelime gibi algılansın
        normalized_text = message.text.replace(', ', ',').replace(' ,', ',')
        parts = normalized_text.split(' ', 2)
        
        if len(parts) < 3:
            bot.reply_to(message, "⚠️ Hatalı kullanım!\nDoğru kullanım:\n`/gonder +905551234567,+905551234568 Mesajınız`", parse_mode='Markdown')
            return
            
        phone = parts[1].strip()
        text = parts[2].strip()
        
        # Doğrudan arka plana gönder

        thread = threading.Thread(target=send_whatsapp_message, args=(message.chat.id, phone, text))
        thread.start()

    except Exception as e:
        bot.reply_to(message, f"❌ Komut işlenirken hata oluştu: {str(e)}")


if __name__ == "__main__":
    print("🤖 Telegram Dinleyici Bot Çalışıyor... (Çıkış yapmak için CTRL+C)")
    # Sonsuz döngüde Telegram'dan gelecek mesajları bekle
    bot.infinity_polling()
