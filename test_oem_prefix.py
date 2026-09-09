"""OEM etiket öneki ve logo yolu kontrolü: python test_oem_prefix.py"""
import os

from backend.utils import Utils

utils = Utils(None)

# Ford yeni eklendi, Arçelik/Watt bozulmadı
assert utils.get_oem_label_prefix({"LOGO_NAME": "ford_logo"}) == "FORD"
assert utils.get_oem_label_prefix({"LOGO_NAME": "arcelikbywat_logo"}) == "ARÇELİK"
assert utils.get_oem_label_prefix({"LOGO_NAME": "wat_logo"}) == "ARÇELİK"

# OEM olmayan / eksik logo ikinci etiket bastırmamalı
assert utils.get_oem_label_prefix({"LOGO_NAME": "hera_logo"}) is None
assert utils.get_oem_label_prefix({}) is None

# Yazıcı adları önekten türetiliyor
prefix = utils.get_oem_label_prefix({"LOGO_NAME": "ford_logo"})
assert f"{prefix} ARKA MASA" == "FORD ARKA MASA"
assert f"{prefix} ÖN MASA" == "FORD ÖN MASA"
assert f"{prefix} PAKET" == "FORD PAKET"

# Var olan logo bulunmalı, olmayan için de database/images altında yol üretilmeli
mevcut = utils.get_image_path("wat_logo.png")
assert os.path.exists(mevcut), f"wat_logo.png bulunamadı: {mevcut}"

yok = utils.get_image_path("boyle_bir_logo_yok.png")
assert not os.path.exists(yok)
assert yok.endswith(os.path.join("database", "images", "boyle_bir_logo_yok.png")), yok

print("OK")
