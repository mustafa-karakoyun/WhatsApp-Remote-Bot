# WhatsApp Remote Bot 🤖📱

**Telegram üzerinden komut vererek WhatsApp Web'i arka planda (headless) yönetmenizi sağlayan gelişmiş otomasyon aracı.**

Bu proje, bilgisayarınızdan uzaktayken bile telefonunuzdaki Telegram aracılığıyla WhatsApp mesajları (tekli veya çoklu) gönderebilmenizi sağlar. Selenium tabanlıdır ve banlanma riskini en aza indirmek için "İnsan Davranışı Simülasyonu" kullanır.

---

## 🌟 Öne Çıkan Özellikler

* **Uzaktan Kontrol:** Sadece yetkilendirdiğiniz Telegram hesabından gelen emirleri dinler. Dünyanın her yerinden bilgisayarınıza WhatsApp komutu verebilirsiniz.
* **Toplu Gönderim:** Virgülle ayırdığınız sınırsız sayıdaki numaraya sırayla mesaj iletebilir.
* **Arka Plan (Headless) Modu:** Chrome tarayıcısı ekranınızda görünmez, işinizi bölmeden arka planda sessizce çalışır.
* **Akıllı Oturum (Session) Yönetimi:** `whatsapp_profile` klasörü sayesinde QR kodu sadece ilk seferde okutursunuz. Bot kapanıp açılsa bile oturum açık kalır.
* **Anti-Ban (İnsan Simülasyonu):** Mesajları saniyesinde yapıştırmak yerine, klavyeden insan gibi tuşlama (yazıyor...) animasyonuyla yazar ve aralara rastgele saniyeler ekler.

---

## ⚙️ Kurulum

### 1. Gereksinimler
* Python 3.8 veya üzeri
* Google Chrome Tarayıcı

### 2. Projeyi İndirme
```bash
git clone https://github.com/mustafa-karakoyun/WhatsApp-Remote-Bot.git
cd WhatsApp-Remote-Bot
```

### 3. Kütüphaneleri Yükleme
```bash
pip install selenium webdriver-manager python-dotenv pyyaml requests pyTelegramBotAPI
```

---

## 🔐 Telegram Botu Ayarlama

Botu uzaktan kontrol edebilmeniz için kendi Telegram botunuzu yaratmanız gerekir. Bu işlem 2 dakika sürer:

### Adım 1: Bot Token Alma
1. Telegram'da arama çubuğuna **`@BotFather`** yazın ve mavi tikli bota tıklayın.
2. Mesaj olarak `/newbot` gönderin.
3. Botunuz için bir isim ve sonu `bot` ile biten bir kullanıcı adı (Örn: `benim_wp_bot`) belirleyin.
4. BotFather size uzun bir şifre (Token) verecektir. *(Örnek: 123456789:ABCDEF...)*

### Adım 2: Kendi Chat ID'nizi Öğrenme
Başkalarının botunuzu kullanmasını engellemek için kendi ID'nizi bulmalısınız:
1. Telegram arama çubuğuna **`@userinfobot`** yazın ve başlatın.
2. Size bir `Id` numarası verecektir. *(Örnek: 1335693229)*

### Adım 3: .env Dosyasını Oluşturma
Proje klasörünüzün içine (botV2.py'nin yanına) **`.env`** adında yeni bir dosya oluşturun ve içine az önce aldığınız bilgileri şu şekilde yazın:

```env
TELEGRAM_BOT_TOKEN="BotFather_dan_aldiginiz_token"
TELEGRAM_CHAT_ID="Sizin_Chat_ID_Numaraniz"
```

> **ÖNEMLİ:** Telegram'da kendi oluşturduğunuz botu aratıp mutlaka bir kez **"BAŞLAT (Start)"** tuşuna basmayı unutmayın, yoksa bot size cevap dönemez!

---

## 🚀 Kullanım

### Normal (Manuel) Başlatma
Terminali açıp aşağıdaki komutu girdiğinizde dinleyici bot çalışmaya başlar:
```bash
python telegram_listener.py
```
*(İlk çalıştırmada arka planda bir Chrome açılabilir ve sizden WhatsApp QR kodunu telefonunuzdan okutmanızı isteyebilir. Bir kere okuttuktan sonra sistem tamamen otomatikleşir).*

### Telegram'dan Komut Verme
Dinleyici açıkken Telegram botunuza şu mesajı atın:
```text
/gonder +905551234567,+905557654321 Merhaba, yarın toplantıyı unutmayalım!
```
Bot uyanacak, arka planda WhatsApp'ı açacak, sırayla numaralara mesajı atacak ve size "İşlem Tamamlandı" diye rapor dönecektir.

---

## 🤖 Otomasyon: Windows'ta 7/24 Otomatik Çalıştırma

Terminal siyah ekranının sürekli açık kalmasını istemiyorsanız veya bilgisayarınız her açıldığında botun otomatik olarak arka planda (görünmez şekilde) devreye girmesini istiyorsanız şu adımları izleyin:

### Yöntem 1: Başlangıç Klasörü (En Kolay Yöntem)
1. Proje klasörünüze gidin ve `baslat.bat` adında yeni bir metin belgesi oluşturun.
2. İçine şu kodu yazıp kaydedin (yolları kendi bilgisayarınıza göre düzeltin):
   ```bat
   @echo off
   cd C:\Users\SizinAdiniz\Desktop\WhatsApp-Remote-Bot
   start pythonw.exe telegram_listener.py
   ```
   *(Not: `pythonw.exe` komutu, Python'u siyah terminal ekranı çıkarmadan tamamen arka planda gizli çalıştırır).*
3. Klavyeden `Windows + R` tuşlarına basın, `shell:startup` yazıp Enter'a basın.
4. Oluşturduğunuz `baslat.bat` dosyasının kısayolunu bu açılan klasörün içine sürükleyin.
**Sonuç:** Artık bilgisayarı her açtığınızda bot sessizce dinlemeye başlayacaktır.

### Yöntem 2: Windows Görev Zamanlayıcı (Task Scheduler)
1. Başlat menüsüne "Görev Zamanlayıcı" yazın ve açın.
2. Sağ taraftan **"Temel Görev Oluştur"**a tıklayın.
3. İsim: `Telegram WhatsApp Bot`
4. Tetikleyici: **"Oturum açtığımda"** veya **"Bilgisayar başladığında"** seçin.
5. Eylem: **"Program başlat"**
6. Program/Arama betiği kısmına: `pythonw.exe` yazın.
7. Bağımsız değişkenler kısmına: `telegram_listener.py` yazın.
8. Başlama yeri kısmına: Proje klasörünüzün tam yolunu (Örn: `C:\Users\karak\Desktop\WhatBot`) yazın.
9. Görevi kaydedin. Artık siz bilgisayarı açtığınız an sistem tamamen arka planda dinlemede olacaktır!

---

## ⚠️ Yasal Uyarı (Disclaimer)
Bu proje sadece eğitim ve araştırma amacıyla geliştirilmiştir. WhatsApp'ın Hizmet Şartları'na (TOS) aykırı olarak yapılabilecek spam, rahatsız edici mesajlar veya kötüye kullanım durumlarında tüm sorumluluk yazılımı kullanan kişiye aittir. Otomasyon araçları kullanırken lütfen her zaman WhatsApp'ın hız limitlerine ve kurallarına uyun.
