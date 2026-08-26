# Yol Haritası · Kripto Sistemi

*Güncelleme: 25.08.2026*

Doğukan Doğan'ın 4 sisteminden, senin kısıtlarına (Binance yok, kaldıraç
yok, Midas spot, 3 ay tecrübe) uyarlanmış tek sistem.

---

## ✅ BİTTİ

### 1 · Bağlam katmanı (Doc 3'ten)
- `baglam/profilim.md` — mülakattan dolduruldu
- `baglam/kurallarim.md` — dolduruldu + **4 çelişki** ayrı bölüm olarak işlendi
- `baglam/hata-muzem.md` — 260 TL dersi, 4 tekrarlayan hata, 2 uyarı cümlesi,
  "henüz yapmadığın ama riskli" bölümü, karar öncesi 3 soru
- `baglam/portfoyum.csv` — boş (şu an pozisyon yok), yapısı hazır
- `baglam/radarim.md` — BTC/ETH/SOL/XRP eklendi
- `baglam/promptlar.md` — 6 prompt, futures kısımları çıkarılmış

### 2 · Nöbet katmanı (Doc 1'in otomatik tarama kısmı)
- `nobet.py` — iki kademeli. Kademe 1 saf Python (model yok, maliyet yok);
  Kademe 2 yalnızca eşik aşılınca Claude'u çağırır
- `esikler.yml` — coin bazında eşik (BTC %5, ETH %6, SOL/XRP %8),
  USD + TL gösterim, gün bazında çalışma pencereleri, yön filtresi,
  yorum modeli (claude-sonnet-4-6 / effort medium), spam sessizliği
- `.github/workflows/nobet.yml` — **hafta içi 18:00-21:00 saat başı,
  hafta sonu 09:00-21:00 iki saatte bir** (TSİ)
- `state/nobet.json` — 12 saatlik spam önleme hafızası

### 3 · Dayanıklılık
- `.github/workflows/token-watchdog.yml` — Pazartesileri token'ları test eder,
  rapor 7 günde 2+ kez patlarsa Telegram'dan haber verir
- `KURULUM.md` — 6 adım + bilinen kırılma noktaları tablosu

### 4 · Bulunan ve düzeltilen hatalar
| Hata | Belirti | Durum |
|---|---|---|
| Fiyat biçimlendirme | `$1200` → `$1,2` yazıyordu | ✅ düzeltildi |
| `--test` modu çöküyordu | `KeyError: 'fiyatlar'` | ✅ düzeltildi |
| Workflow'da `${KONU}` genişlemiyordu | Claude'a coin adı gitmiyordu | ✅ düzeltildi |
| `actions: read` izni eksikti | Token nöbetçisi patlardı | ✅ düzeltildi |

---

## ⬜ SIRADAKİ İŞLER

### Adım 1 · Kurulum (senin işin, ~30 dk)
- [ ] Zip'i indir
- [ ] `git clone https://github.com/xDoko00/crypto-daily-report-template`
- [ ] Zip'teki dosyaları üstüne kopyala, `requirements.txt`'leri birleştir
- [ ] `python nobet.py --kuru` → CoinGecko'ya ulaşıyor mu?
- [ ] Telegram token'ını **yenile** (eskisi sohbete yapıştırıldı, yanmış durumda)
- [ ] `claude setup-token` çalıştır
- [ ] `python setup.py` → sihirbaz kalanını halleder
- [ ] Repoyu **PRIVATE** yap
- [ ] Actions'tan 3 workflow'u da test modunda çalıştır

### Adım 2 · Claude Projesi (senin işin, ~10 dk)
- [ ] claude.ai → Yeni Proje → "Kripto Araştırma"
- [ ] `baglam/` içindeki 6 dosyayı yükle
- [ ] `profilim.md` + `kurallarim.md` içeriğini proje talimatlarına yapıştır
- [ ] Test: "Hata Kontrolü promptunu çalıştır, XRP almayı düşünüyorum" yaz

### Adım 3 · 7/24 "tara" botu (benim işim, sen seçtin)
Videodaki gibi Telegram'a "tara" yazınca cevap veren bot.

- [ ] `bot.py` — python-telegram-bot ile polling
- [ ] Komutlar: `/tara`, `/durum`, `/kural`, serbest sohbet
- [ ] `baglam/` dosyalarını okur → cevapları senin kurallarınla süzer
- [ ] Ücretsiz sunucu seçimi (Railway / Render / Fly)
- [ ] Deploy dosyaları + kurulum adımları

**Bilmen gerekenler:** Bu, sistemin bakım gerektiren tek parçası olacak.
Ücretsiz katmanlar uykuya geçebilir, aylık saat limiti olabilir, servis
politikası değişebilir. Diğer her şey GitHub Actions'ta çalıştığı için
bakımsız; bot öyle olmayacak.

### Adım 4 · Radar koşulları (senin işin, acelesi yok)
- [ ] `radarim.md` içindeki "ne olursa alırım" sütununu doldur

Bunu şimdi yapmanı beklemiyorum. Sistem kurulsun, birkaç uyarı gelsin, ne
tür hareketlerin dikkatini çektiğini gör; sonra doldur. Uydurma bir koşul
yazmaktansa boş bırakmak daha dürüst.

### Adım 5 · Çeyrek bakımı (Kasım 2026)
- [ ] `promptlar.md` #6'yı çalıştır, üç dosyayı gözden geçir

---

## ❌ BİLEREK YAPILMAYANLAR

| Ne | Neden |
|---|---|
| İşlem kartı (LONG/SHORT, kaldıraç, marj) | Kaldıraçlı hesabın yok. Karşılığı yok |
| ISOLATED marj, kill switch, martingale yasağı | Aynı sebep |
| Ekran görüntüsü okuma | Dubai videosunda model ekran görüntüsünü yanlış okuyup olmayan bir kural ihlali uydurdu. Bilerek dışarıda |
| Tatil Trade Deneyi | Tamamı futures. Disiplin mekanizmaları `hata-muzem.md`'ye taşındı |
| 10 dakikada bir tarama | Videoda sık bildirim aceleye yol açtı (kalan 55 dolarla 27x pozisyon). Bunun yerine hafta içi akşam penceresi seçildi |
| Abacus AI | Aylık 10 dolar. GitHub Actions + Claude aboneliği ile aynı iş 0 dolara yapılıyor |

---

## Sistemin ne yapıp ne yapmadığı

**Yapar:** Her sabah rapor. Eşik aşılınca uyarı. Karar öncesi kendi
kurallarını ve geçmiş hatalarını hatırlatma.

**Yapmaz:** Ne alacağını söylemez. İşlem açmaz. Kazandırma sözü vermez.

Uyarı "eşik aşıldı" demektir, "gir" demez. Ayda birkaç uyarı gelecek;
hepsine işlem yaparsan sistem amacının tam tersine hizmet etmiş olur.

*Yatırım tavsiyesi değildir. Karar ve sorumluluk sana aittir.*
