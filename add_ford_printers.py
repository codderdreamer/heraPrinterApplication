"""ARÇELİK yazıcı kayıtlarını ve etiket tasarımlarını FORD için çoğaltır.

Kullanım: FordKurulum.exe dosyasını HeraPrinterApp.exe'nin yanına koy ve
uygulama KAPALIYKEN çift tıkla. (Geliştirmede: python add_ford_printers.py)

Tekrar çalıştırılabilir: var olan kayıtlara dokunmaz, sadece eksikleri ekler.
"""
import json
import os
import shutil
import sqlite3
import sys
from datetime import datetime

# exe olarak paketlendiğinde CWD'ye değil exe'nin bulunduğu klasöre göre çalış
if getattr(sys, "frozen", False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DB_PATH = os.path.join(BASE_DIR, "database", "database.db")

# Konsol kod sayfası Türkçe karakterleri desteklemiyorsa çökmek yerine '?' yazsın
for _akis in (sys.stdout, sys.stderr):
    if hasattr(_akis, "reconfigure"):
        _akis.reconfigure(errors="replace")

KAYNAK_ONEK = "ARÇELİK"
HEDEF_ONEK = "FORD"
MASALAR = ["ARKA MASA", "ÖN MASA", "PAKET"]


def tasarim_kontrol(hedef_ad, settings_data):
    """Kopyalanan tasarımda elle düzeltilmesi gereken bir şey var mı diye bakar."""
    try:
        ayarlar = json.loads(settings_data)
    except (TypeError, ValueError):
        print(f"    ! {hedef_ad}: tasarım JSON okunamadı, web arayüzünden kontrol et")
        return

    value_items = ayarlar.get("valueItems", [])
    logo_var = any(v.get("valueId") == "LOGO_NAME" for v in value_items)
    if logo_var:
        print(f"    + {hedef_ad}: LOGO_NAME alanı var, ford_logo.png otomatik basılacak")
    else:
        print(f"    ! {hedef_ad}: LOGO_NAME alanı YOK, logo basılmaz. "
              f"Web arayüzünden 'LOGO_NAME' value alanı eklemelisin")

    # Arçelik logosu sabit bir ikon olarak gömülüyse Ford etiketine de gelir
    if ayarlar.get("iconItems"):
        print(f"    ! {hedef_ad}: {len(ayarlar['iconItems'])} adet sabit ikon var, "
              f"Arçelik'e ait olan varsa web arayüzünden sil")

    if "rçelik" in settings_data or "RÇELİK" in settings_data or "rcelik" in settings_data.lower():
        print(f"    ! {hedef_ad}: tasarımda 'Arçelik' yazan sabit metin var, "
              f"web arayüzünden Ford'a çevir")


def main():
    try:
        # Mikrosaniye dahil: tekrar çalıştırıldığında önceki yedeğin üzerine yazmasın
        yedek = f"{DB_PATH}.{datetime.now():%Y%m%d_%H%M%S_%f}.yedek"
        shutil.copy2(DB_PATH, yedek)
        print(f"Yedek alındı: {yedek}\n")
    except FileNotFoundError:
        sys.exit(f"HATA: {DB_PATH} bulunamadı.\n"
                 f"Bu dosyayı HeraPrinterApp.exe ile aynı klasöre koyup tekrar çalıştır.")

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    kolonlar = [k["name"] for k in cur.execute("PRAGMA table_info(bitmap_settings)")]
    if "printer_name" not in kolonlar:
        sys.exit("HATA: bitmap_settings tablosu eski formatta. Önce uygulamayı bir kez "
                 "açıp kapat (migration çalışır), sonra bu scripti tekrar çalıştır.")

    for masa in MASALAR:
        kaynak_ad = f"{KAYNAK_ONEK} {masa}"
        hedef_ad = f"{HEDEF_ONEK} {masa}"
        print(f"{hedef_ad}:")

        kaynak = cur.execute("SELECT * FROM printers WHERE name = ?", (kaynak_ad,)).fetchone()
        if not kaynak:
            print(f"    ! Kaynak yazıcı '{kaynak_ad}' bulunamadı, atlandı")
            continue

        hedef = cur.execute("SELECT * FROM printers WHERE name = ?", (hedef_ad,)).fetchone()
        if hedef:
            print(f"    = Yazıcı kaydı zaten var (ip: {hedef['ip']})")
            hedef_ip = hedef["ip"]
        else:
            cur.execute(
                "INSERT INTO printers (ip, name, dpi, width, height) VALUES (?, ?, ?, ?, ?)",
                (kaynak["ip"], hedef_ad, kaynak["dpi"], kaynak["width"], kaynak["height"]),
            )
            hedef_ip = kaynak["ip"]
            print(f"    + Yazıcı eklendi (ip: {hedef_ip}, {kaynak['width']}x{kaynak['height']}mm, "
                  f"{kaynak['dpi']} dpi)")

        # Kaynak yazıcının tüm etiket tasarımlarını Ford'a kopyala
        tasarimlar = cur.execute(
            "SELECT name, settings_data FROM bitmap_settings WHERE printer_name = ?", (kaynak_ad,)
        ).fetchall()
        if not tasarimlar:
            print(f"    ! '{kaynak_ad}' için kayıtlı tasarım yok, kopyalanacak bir şey bulunamadı")
            continue

        for tasarim in tasarimlar:
            mevcut = cur.execute(
                "SELECT 1 FROM bitmap_settings WHERE printer_name = ? AND name = ?",
                (hedef_ad, tasarim["name"]),
            ).fetchone()
            if mevcut:
                print(f"    = '{tasarim['name']}' tasarımı zaten var, korundu")
                continue

            cur.execute(
                "INSERT INTO bitmap_settings (printer_ip, printer_name, name, settings_data) "
                "VALUES (?, ?, ?, ?)",
                (hedef_ip, hedef_ad, tasarim["name"], tasarim["settings_data"]),
            )
            print(f"    + '{tasarim['name']}' tasarımı kopyalandı")
            tasarim_kontrol(hedef_ad, tasarim["settings_data"])

    conn.commit()
    conn.close()

    print("\nBitti. Sırada:")
    print("  1. database/images/ford_logo.png dosyasını koy")
    print("  2. Ford ayrı bir fiziksel yazıcıya basacaksa, web arayüzünden")
    print("     FORD yazıcılarının IP adresini güncelle (şu an Arçelik'in IP'si kopyalandı)")
    print("  3. Bir Ford seri numarasıyla test yazdırması yap")


if __name__ == "__main__":
    kod = 0
    try:
        main()
    except SystemExit as e:
        if e.code:
            print(e.code)
            kod = 1
    except Exception:
        import traceback
        traceback.print_exc()
        kod = 1

    # Çift tıklayınca pencere kapanıp mesajlar kaybolmasın
    if getattr(sys, "frozen", False):
        try:
            input("\nKapatmak için Enter'a bas...")
        except EOFError:
            pass
    sys.exit(kod)
