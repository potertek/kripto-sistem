# Prompt Kütüphanesi

Bu altı promptu Claude Projesi içinde kullan. Proje `baglam/` klasörünü
gördüğü için her seferinde kim olduğunu anlatman gerekmiyor.

Kaldıraç/futures promptları bilerek çıkarıldı — spot çalışıyorsun.

---

## 1 · Sabah Brifingi

*Nöbet sana zaten uyarı gönderiyor. Bu prompt farklı: uyarıyı değil,
gecenin toplamını verir.*

```
Sabah brifingimi ver: gece boyunca BTC, ETH ve piyasa geneli ne yaptı,
en çok yükselen ve düşen coinler, korku-açgözlülük endeksi, radarımdaki
coinlerle ilgili haberler.
Sonra bunları portfoyum.csv ve profilim.md'ye göre değerlendir: hangisi
benim varlıklarımı etkiliyor, bugün dikkat etmem gereken tek şey ne.
En fazla 10 madde, telefonda 60 saniyede okunsun.
Verdiğin her sayının kaynağını belirt.
```

---

## 2 · Coin Röntgeni

```
$COIN hakkında tam bir röntgen çek: güncel fiyat ve bu ay nasıl hareket
etti, piyasa değeri ve hacim, dolaşımdaki arz ile toplam arz farkı,
projenin ne yaptığı, son dönemdeki gelişmeler ve kırmızı bayraklar.
Bana bunu almam gerekip gerekmediğini söyleme; neye bakmam gerektiğini
söyle.
```

---

## 3 · Karşılaştırma

```
$A ile $B'yi karşılaştır: piyasa değeri, hacim, arz yapısı, son 1 yıl
performansı, ekosistem büyüklüğü ve riskler.
Karşılaştırma tablosu yap, sonra her ikisinin de en güçlü ve en zayıf
yanını söyle. Kazanan ilan etme.
```

---

## 4 · FUD Kontrol

```
Şu iddiayı duydum: "[iddiayı buraya yaz]". Bunu doğrula.
Kaynak var mı, kim söylemiş, ne zaman söylenmiş, resmî bir açıklama mı
yoksa söylenti mi.
Doğrulayamıyorsan "doğrulanamadı" de, tahmin yürütme.
Bu haber gerçekse portföyümü nasıl etkiler, onu da söyle.
```

---

## 5 · Hata Kontrolü ⭐

*Sistemin en önemli promptu. Bir karar vermeden ÖNCE çalıştır.*

```
Şunu yapmayı düşünüyorum: "[ne yapmak istediğini yaz]".
Karar vermeden önce hata-muzem.md ve kurallarim.md dosyalarını oku.
Bu hareket geçmişte yaptığım hatalardan birine benziyor mu?
Kurduğum cümlelerden biri uyarı cümlelerimden biri mi?
Kendi kurallarımdan hangisini çiğnemek üzereyim?
Bana yağ çekme, dürüst cevap ver. Sorun yoksa "sorun yok" de.
```

---

## 6 · Çeyrek Bakımı

*3 ayda bir. Takvime kur — eski profil sessizce her cevabı bozar.*

```
Profilimi, kurallarımı ve hata müzemi benimle birlikte gözden geçir.
Son 3 ayda değişen bir şey var mı: gelirim, risk toleransım, hedeflerim?
Yeni bir hata yaptım mı, müzeye eklemem gereken bir şey var mı?
Tek tek sor, cevaplarımı dosyalara işle.
```

---

## Güven kuralı — her prompt için

Yapay zekâ sana canlı veri bağlantısı kullanmadan rakam veriyorsa, o
rakamlar hafızasından gelmiş ve eski olabilir.

Sor: **"Bu rakamların her birini nereden aldın?"**

Cevap veremiyorsa o rakama güvenme. Kripto fiyatları dakikalar içinde
değişir.

Bu kuralın neden var olduğunun somut örneği: Doğukan'ın Dubai videosunda
model, gönderilen ekran görüntüsünü yanlış okuyup olmayan bir kural ihlali
uydurdu ("cross 20x yapmışsın"). Model kendinden emin görünürken de
yanılabilir.
