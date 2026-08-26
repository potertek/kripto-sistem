#!/usr/bin/env python3
"""
nobet.py — Gün içi nöbet katmanı.

Tasarım ilkesi: SAYIYA MODEL DOKUNMAZ.
  Kademe 1 (her koşuda): saf Python + CoinGecko. Eşik aşılmadıysa
                         hiç mesaj atmaz, hiç model çağırmaz. Maliyet sıfır.
  Kademe 2 (sadece eşik aşılınca): workflow, Claude'u çağırıp "neden
                         hareket etti" yorumunu ayrı bir mesaj olarak ekler.

Kademe 1 başarısız olursa Kademe 2 hiç çalışmaz. Kademe 2 başarısız olursa
Kademe 1'in gönderdiği rakamlar yine elindedir. Tek nokta arızası yok.

Kullanım:
    python nobet.py            # normal koşu
    python nobet.py --test     # eşik aşılmasa da örnek uyarı gönderir
    python nobet.py --kuru     # hiçbir şey göndermez, ekrana basar
"""

from __future__ import annotations

import csv
import json
import os
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import requests
import yaml

KOK = Path(__file__).resolve().parent
BAGLAM = KOK / "baglam"
DURUM_DOSYASI = KOK / "state" / "nobet.json"
ESIK_DOSYASI = KOK / "esikler.yml"

TSI = timezone(timedelta(hours=3))
COINGECKO = "https://api.coingecko.com/api/v3/simple/price"
FNG = "https://api.alternative.me/fng/"
ZAMAN_ASIMI = 20


# --------------------------------------------------------------------------
# Yardımcılar
# --------------------------------------------------------------------------

def simdi() -> datetime:
    return datetime.now(TSI)


def esikleri_oku() -> dict:
    with ESIK_DOSYASI.open(encoding="utf-8") as f:
        return yaml.safe_load(f)


def durum_oku() -> dict:
    if not DURUM_DOSYASI.exists():
        return {}
    try:
        return json.loads(DURUM_DOSYASI.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        # Bozuk state dosyası nöbeti durdurmasın; sıfırdan başla.
        return {}


def durum_yaz(durum: dict) -> None:
    DURUM_DOSYASI.parent.mkdir(parents=True, exist_ok=True)
    DURUM_DOSYASI.write_text(
        json.dumps(durum, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def calisma_penceresinde_mi(esikler: dict, an: datetime) -> tuple[bool, str]:
    """(pencere_icinde_mi, aciklama) döner. Hafta içi/sonu ayrı pencere."""
    pencereler = esikler["calisma_saatleri"]
    hafta_sonu = an.weekday() >= 5           # 5=Cumartesi, 6=Pazar
    anahtar = "hafta_sonu" if hafta_sonu else "hafta_ici"
    p = pencereler[anahtar]
    icinde = p["baslangic"] <= an.hour < p["bitis"]
    etiket = "hafta sonu" if hafta_sonu else "hafta içi"
    return icinde, f"{etiket} penceresi {p['baslangic']:02d}:00-{p['bitis']-1:02d}:59"


def yon_uygun_mu(degisim: float, filtre: str) -> bool:
    if filtre == "sadece_dusus":
        return degisim < 0
    if filtre == "sadece_yukselis":
        return degisim > 0
    return True


def sessizlikte_mi(durum: dict, anahtar: str, saat: int) -> bool:
    """Bu uyarı yakın zamanda gönderildi mi? (spam önleme)"""
    kayit = durum.get(anahtar)
    if not kayit:
        return False
    try:
        son = datetime.fromisoformat(kayit)
    except ValueError:
        return False
    return simdi() - son < timedelta(hours=saat)


# --------------------------------------------------------------------------
# Bağlam dosyalarını oku
# --------------------------------------------------------------------------

def portfoy_coinleri() -> list[str]:
    dosya = BAGLAM / "portfoyum.csv"
    if not dosya.exists():
        return []
    coinler = []
    with dosya.open(encoding="utf-8") as f:
        for satir in csv.DictReader(f):
            sembol = (satir.get("coin") or "").strip().upper()
            not_alani = (satir.get("not") or "").lower()
            if sembol and "ornek" not in not_alani and "örnek" not in not_alani:
                coinler.append(sembol)
    return coinler


def radar_coinleri() -> list[str]:
    """radarim.md içindeki markdown tablosunun ilk sütununu okur."""
    dosya = BAGLAM / "radarim.md"
    if not dosya.exists():
        return []
    coinler = []
    for satir in dosya.read_text(encoding="utf-8").splitlines():
        if not satir.strip().startswith("|"):
            continue
        hucreler = [h.strip() for h in satir.strip().strip("|").split("|")]
        if not hucreler:
            continue
        sembol = hucreler[0].upper()
        if not re.fullmatch(r"[A-Z0-9]{2,10}", sembol):
            continue
        if sembol in {"COIN", "ÖRNEK", "ORNEK"}:
            continue
        coinler.append(sembol)
    return coinler


# --------------------------------------------------------------------------
# Veri çekme
# --------------------------------------------------------------------------

def fiyatlari_cek(
    semboller: list[str], harita: dict, birimler: list[str]
) -> dict:
    """{SEMBOL: {"usd": float, "try": float, "degisim": float}} döner."""
    idler = [harita[s] for s in semboller if s in harita]
    if not idler:
        return {}

    ana = birimler[0]  # değişim yüzdesi ana birimden okunur
    yanit = requests.get(
        COINGECKO,
        params={
            "ids": ",".join(sorted(set(idler))),
            "vs_currencies": ",".join(birimler),
            "include_24hr_change": "true",
        },
        timeout=ZAMAN_ASIMI,
    )
    yanit.raise_for_status()
    ham = yanit.json()

    sonuc = {}
    for sembol in semboller:
        cg_id = harita.get(sembol)
        veri = ham.get(cg_id) if cg_id else None
        if not veri or veri.get(ana) is None:
            continue
        kayit = {"degisim": float(veri.get(f"{ana}_24h_change") or 0.0)}
        for b in birimler:
            if veri.get(b) is not None:
                kayit[b] = float(veri[b])
        sonuc[sembol] = kayit
    return sonuc


def fear_greed_cek() -> tuple[int, str] | None:
    try:
        yanit = requests.get(FNG, params={"limit": 1}, timeout=ZAMAN_ASIMI)
        yanit.raise_for_status()
        kayit = yanit.json()["data"][0]
        return int(kayit["value"]), kayit.get("value_classification", "")
    except (requests.RequestException, KeyError, ValueError, IndexError):
        # F&G ikincil veri; alınamazsa nöbet fiyatlarla devam etsin.
        return None


# --------------------------------------------------------------------------
# Telegram
# --------------------------------------------------------------------------

def telegram_gonder(metin: str) -> bool:
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "")
    hedef = os.environ.get("TELEGRAM_ADMIN_CHAT_ID", "")
    if not token or not hedef:
        print("HATA: TELEGRAM_BOT_TOKEN veya TELEGRAM_ADMIN_CHAT_ID tanımlı değil.")
        return False
    try:
        yanit = requests.post(
            f"https://api.telegram.org/bot{token}/sendMessage",
            json={
                "chat_id": hedef,
                "text": metin,
                "parse_mode": "HTML",
                "disable_web_page_preview": True,
            },
            timeout=ZAMAN_ASIMI,
        )
        yanit.raise_for_status()
        return True
    except requests.RequestException as hata:
        print(f"HATA: Telegram gönderimi başarısız: {hata}")
        return False


# --------------------------------------------------------------------------
# Kademe 1: eşik kontrolü
# --------------------------------------------------------------------------

def tetikleri_bul(esikler: dict, durum: dict) -> list[dict]:
    harita = esikler["coingecko_id_haritasi"]
    portfoy = portfoy_coinleri()
    radar = [c for c in radar_coinleri() if c not in portfoy]

    bilinmeyen = [c for c in portfoy + radar if c not in harita]
    if bilinmeyen:
        print(f"UYARI: esikler.yml'de id'si olmayan coinler atlandı: {bilinmeyen}")

    tetikler: list[dict] = []
    birimler = esikler.get("para_birimleri") or ["usd"]
    ozel = esikler.get("coin_esikleri") or {}
    filtre = esikler.get("yon_filtresi", "her_ikisi")
    fiyatlar = fiyatlari_cek(portfoy + radar, harita, birimler)

    for grup, coinler in (("portfoy", portfoy), ("radar", radar)):
        varsayilan = esikler[grup]["degisim_yuzde"]
        sessizlik = esikler[grup]["sessizlik_saat"]
        for sembol in coinler:
            limit = float(ozel.get(sembol, varsayilan))
            veri = fiyatlar.get(sembol)
            if not veri or abs(veri["degisim"]) < limit:
                continue
            if not yon_uygun_mu(veri["degisim"], filtre):
                continue
            anahtar = f"{grup}:{sembol}"
            if sessizlikte_mi(durum, anahtar, sessizlik):
                continue
            tetikler.append({
                "anahtar": anahtar,
                "tur": grup,
                "sembol": sembol,
                "esik": limit,
                "degisim": veri["degisim"],
                "fiyatlar": {b: veri[b] for b in birimler if b in veri},
            })

    fng = fear_greed_cek()
    if fng:
        deger, etiket = fng
        alt = esikler["piyasa"]["fear_greed_alt"]
        ust = esikler["piyasa"]["fear_greed_ust"]
        if (deger <= alt or deger >= ust) and not sessizlikte_mi(
            durum, "piyasa:fng", esikler["piyasa"]["sessizlik_saat"]
        ):
            tetikler.append({
                "anahtar": "piyasa:fng",
                "tur": "piyasa",
                "sembol": "F&G",
                "deger": deger,
                "etiket": etiket,
            })

    return tetikler


SIMGELER = {"usd": "$", "try": "₺", "eur": "€"}


def fiyat_yaz(deger: float, birim: str = "usd") -> str:
    """Büyük fiyatta 2, küçük fiyatta 4-6 basamak. Sondaki sıfırları kırpar."""
    if deger >= 100:
        metin = f"{deger:,.2f}"
    elif deger >= 1:
        metin = f"{deger:,.4f}"
    else:
        metin = f"{deger:,.6f}"
    if "." in metin:
        metin = metin.rstrip("0").rstrip(".")
    return f"{SIMGELER.get(birim, )}{metin}"


def mesaj_kur(tetikler: list[dict]) -> str:
    zaman = simdi().strftime("%d.%m.%Y %H:%M")
    satirlar = [f"<b>NÖBET · {zaman} TSİ</b>", ""]

    for t in tetikler:
        if t["tur"] == "piyasa":
            satirlar.append(
                f"⚖️ <b>Korku/Açgözlülük: {t['deger']}</b> ({t['etiket']})"
            )
            continue
        ok = "🔺" if t["degisim"] > 0 else "🔻"
        etiket = "portföyünde" if t["tur"] == "portfoy" else "radarında"
        fiyat_metni = "  ·  ".join(
            fiyat_yaz(deger, birim) for birim, deger in t["fiyatlar"].items()
        )
        satirlar.append(
            f"{ok} <b>{t['sembol']}</b> ({etiket})  {t['degisim']:+.1f}%  "
            f"<i>(eşik {t['esik']:.0f}%)</i>\n     {fiyat_metni}"
        )

    satirlar += [
        "",
        "<i>Bu bir işlem önerisi değil. Eşik aşıldı, haberin olsun diye yazıyorum.</i>",
        "<i>Karar vermeden önce Hata Kontrolü promptunu çalıştır.</i>",
    ]
    return "\n".join(satirlar)


# --------------------------------------------------------------------------
# Ana akış
# --------------------------------------------------------------------------

def main() -> int:
    test = "--test" in sys.argv
    kuru = "--kuru" in sys.argv

    esikler = esikleri_oku()
    su_an = simdi()

    if not test:
        icinde, aciklama = calisma_penceresinde_mi(esikler, su_an)
        if not icinde:
            print(f"Çalışma saati dışı ({su_an:%H:%M} TSİ, {aciklama}). Sessiz kalınıyor.")
            return 0

    durum = durum_oku()

    try:
        tetikler = tetikleri_bul(esikler, durum)
    except requests.RequestException as hata:
        print(f"HATA: Veri çekilemedi: {hata}")
        return 1  # workflow bunu görsün, Kademe 2 çalışmasın

    if test and not tetikler:
        tetikler = [{
            "anahtar": "test:BTC", "tur": "radar", "sembol": "BTC",
            "esik": 0.0, "degisim": 0.0,
            "fiyatlar": {"usd": 0.0, "try": 0.0},
        }]
        print("TEST modu: gerçek tetik yok, örnek uyarı üretildi.")

    if not tetikler:
        print(f"Eşik aşılmadı ({su_an:%H:%M} TSİ). Mesaj yok, model çağrılmadı.")
        return 0

    mesaj = mesaj_kur(tetikler)
    print(mesaj)

    if kuru:
        print("\n[kuru mod] Gönderim yapılmadı, state güncellenmedi.")
        return 0

    if not telegram_gonder(mesaj):
        return 1  # gönderilemediyse state'i kirletme, sonraki koşu tekrar denesin

    if not test:
        for t in tetikler:
            durum[t["anahtar"]] = su_an.isoformat()
        durum_yaz(durum)

    # Kademe 2 için workflow'a sinyal
    cikti = os.environ.get("GITHUB_OUTPUT")
    if cikti:
        ozet = ", ".join(
            t["sembol"] for t in tetikler if t["tur"] != "piyasa"
        ) or "piyasa geneli"
        with open(cikti, "a", encoding="utf-8") as f:
            f.write("tetiklendi=true\n")
            f.write(f"konu={ozet}\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())
