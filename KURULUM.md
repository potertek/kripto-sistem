# Kurulum

Bu klasör **template'in üstüne** eklenecek katmanları içeriyor. Template'in
kendisini (report.py, kart.py, ses.py, setup.py) indirmen gerekiyor.

---

## 1 · Template'i al

```bash
git clone https://github.com/xDoko00/crypto-daily-report-template kripto-sistem
cd kripto-sistem
rm -rf .git
```

## 2 · Bu klasördeki dosyaları üstüne kopyala

Şunlar **yeni** dosyalar, hiçbirini ezmez:

```
esikler.yml
nobet.py
KURULUM.md
baglam/                          (6 dosya)
.github/workflows/nobet.yml
.github/workflows/token-watchdog.yml
state/nobet.json
```

`requirements.txt` **birleştirilecek** — template'inkinde `Pillow`,
`edge-tts`, `tzdata` var; bizimkinde `PyYAML`. İkisini tek dosyada topla:

```
requests
Pillow
edge-tts
tzdata
PyYAML>=6.0
```

## 3 · Bağlam dosyaları

`profilim.md`, `kurallarim.md`, `hata-muzem.md` **dolu** — mülakattan geldi.

`portfoyum.csv` bilerek boş (şu an pozisyon yok). Aldığında satır ekle:
```
coin,isim,tur,oran_yuzde,ortalama_maliyet,not
SOL,Solana,spot,20,5600,ilk alim
```

`radarim.md` içinde BTC/ETH/SOL/XRP var ama **"ne olursa alırım" sütunu
boş.** Bu sütunu doldurmadan sistem yarım çalışır — uyarı geldiğinde
kararı yine anlık his verir. 260 TL'lik ders tam olarak buradan çıkmıştı.

## 4 · Yerel test (token gerektirmez)

```bash
pip install -r requirements.txt
python nobet.py --kuru
```

`--kuru` hiçbir mesaj göndermez, ekrana basar. CoinGecko'ya gerçekten
ulaşıp ulaşmadığını burada görürsün. Çıktıda coin listen görünmüyorsa
`portfoyum.csv` / `radarim.md` / `esikler.yml` eşleşmesi bozuktur.

## 5 · Sihirbazı çalıştır

```bash
python setup.py
```

Sihirbaz Telegram ve Claude token'ını senden ister, chat_id'leri bulur,
test mesajı atar, `.env` yazar, GitHub reposunu kurar ve 4 secret'ı ekler.

**Repoyu PRIVATE yap.** İçinde portföy verin var.

## 6 · Beşinci secret'ı elle ekle

Sihirbaz 4 secret ekliyor. Nöbet için ekstra bir şey gerekmiyor — aynı
4'ünü kullanıyor:

| Secret | Kim kullanıyor |
|---|---|
| `TELEGRAM_BOT_TOKEN` | rapor + nöbet + nöbetçi |
| `TELEGRAM_CHAT_ID` | rapor (kanal) |
| `TELEGRAM_ADMIN_CHAT_ID` | nöbet + nöbetçi (sana özel) |
| `CLAUDE_CODE_OAUTH_TOKEN` | rapor + nöbet kademe 2 |

## 7 · Uçtan uca test

GitHub → Actions:

- **Nöbet** → Run workflow → mod: `test` → sana örnek uyarı gelmeli
- **Günlük Kripto Raporu** → Run workflow → mode: `test` → sana rapor gelmeli
- **Token Nöbetçisi** → Run workflow → yeşil olmalı

Üçü de yeşilse sistem canlı.

---

## Claude Projesi (4. katman)

Nöbet ve rapor otomatik. Karar kontrolü ise sohbette çalışıyor:

1. claude.ai → yeni Proje → "Kripto Araştırma"
2. `baglam/` içindeki 6 dosyayı projeye yükle
3. `profilim.md` + `kurallarim.md` içeriğini **proje talimatlarına** yapıştır
4. `promptlar.md` içindeki 6 promptu kopyala-yapıştır kullan

Bir karar vermeden önce **5 numaralı Hata Kontrolü** promptunu çalıştır.

---

## Bilinen kırılma noktaları

| Ne olur | Belirti | Çözüm |
|---|---|---|
| Claude token süresi dolar | Rapor sessizce gelmez | `claude setup-token` → secret'ı güncelle |
| GitHub cron gecikir | Rapor 08:00 yerine 08:20 | Normal. Ücretsiz zamanlayıcının doğası |
| CoinGecko limiti | Nöbet 429 alır | Sıklığı azalt. 2 saatte bir ≈ 7 çağrı/gün, limit 10.000/ay |
| `esikler.yml` id eksik | Coin uyarı vermez | Loglarda "id'si olmayan coinler atlandı" satırını ara |
| state commit çakışması | Nöbet push hatası | `concurrency` bunu engelliyor; tekrar eden hatada state/nobet.json'u sıfırla |

Token Nöbetçisi ilk üçünü Pazartesi sabahları kontrol edip sana yazıyor.

---

*Bu sistem yatırım tavsiyesi vermez. Veri toplar, eşik aşıldığında haber
verir ve karar öncesinde kendi kurallarını hatırlatır. Karar ve sorumluluk
sana aittir.*
