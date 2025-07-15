from PySide6.QtGui import QFontDatabase
import os


def load_vazirmatn_font():
    font_dir = os.path.join(os.path.dirname(__file__), "..", "resources", "fonts")
    font_path = os.path.join(font_dir, "Vazirmatn-Regular.ttf")

    font_id = QFontDatabase.addApplicationFont(font_path)
    # if font_id == -1:
    #     print("❌ بارگذاری فونت وزیرمتن ناموفق بود.")
    # else:
    #     font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
    #     print(f"✅ فونت {font_family} بارگذاری شد.")
