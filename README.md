# WhatsApp Remote Bot 🤖

A headless WhatsApp automation bot remotely controlled via Telegram commands. Powered by Selenium.

## Özellikler (Features)

* **Telegram Uzaktan Kontrolü:** Bilgisayarınızdan uzakta olsanız bile Telegram üzerinden komut vererek WhatsApp'tan mesaj atabilirsiniz.
* **Toplu Mesaj Gönderimi:** Tek bir komutla birden fazla numaraya otomatik gecikmeler (anti-ban) uygulayarak mesaj gönderme.
* **Arka Plan (Headless) Çalışma:** Uygulama Chrome'u arka planda gizlice çalıştırır, ekranınızı meşgul etmez.
* **Akıllı Oturum Yönetimi:** QR kodu sadece ilk seferde bir kez okutmanız yeterlidir, sonrasında oturum otomatik olarak hatırlanır.
* **İnsan Davranışı Simülasyonu:** Rastgele yazma hızları ve bekleme süreleri ile WhatsApp algoritmaları tarafından robot olduğunun anlaşılması (banlanma) engellenir.

## Kurulum (Installation)

1. Projeyi bilgisayarınıza klonlayın:
```bash
git clone https://github.com/mustafa-karakoyun/WhatsApp-Remote-Bot.git
cd WhatBot
```

2. Gerekli Python kütüphanelerini kurun:
```bash
pip install selenium webdriver-manager python-dotenv pyyaml requests pyTelegramBotAPI
```

3. Gizli ayar dosyanızı oluşturun:
Proje ana dizinine bir `.env` dosyası açın ve içerisine Telegram bot bilgilerinizi ekleyin:
```env
TELEGRAM_BOT_TOKEN="sizin_bot_tokeniniz"
TELEGRAM_CHAT_ID="sizin_chat_id_numaraniz"
```

## Nasıl Kullanılır? (Usage)

1. Terminali açın ve dinleyici botu çalıştırın:
```bash
python telegram_listener.py
```

2. Telegram'ı açın ve kendi botunuza şu formatta bir mesaj gönderin:
```text
/gonder +905551234567,+905557654321 Merhaba, yarınki toplantıyı unutmayalım!
```

Bot anında uyanacak, WhatsApp'ı arka planda açacak ve belirttiğiniz numaralara sırayla mesajınızı iletip size Telegram üzerinden Rapor gönderecektir!

## Uyarı (Disclaimer)
Bu proje eğitim amaçlı geliştirilmiştir. WhatsApp'ın Hizmet Şartları'na (TOS) aykırı olarak spam veya kötüye kullanım durumlarında sorumluluk tamamen kullanıcıya aittir. Otomasyon araçları kullanırken her zaman makul hız limitlerine uyun.
