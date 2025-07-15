import sys
import os
from PySide6.QtWidgets import QApplication, QMainWindow, QMessageBox
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile, Qt
from PySide6.QtGui import QFontDatabase

from core.font_loader import load_vazirmatn_font
from core.auth import master_exists, save_master_password, check_master_password
from core.auth import set_current_password


class LoginWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        loader = QUiLoader()
        ui_file = QFile("ui/login.ui")
        ui_file.open(QFile.ReadOnly)
        self.ui = loader.load(ui_file, self)
        ui_file.close()

        self.setCentralWidget(self.ui)
        self.setWindowTitle("رمزتو - ورود")
        self.setFixedSize(400, 250)

        self.ui.btn_login.clicked.connect(self.handle_login)
        self.ui.lineEdit_password.returnPressed.connect(self.ui.btn_login.click)

    def handle_login(self):
        password = self.ui.lineEdit_password.text().strip()
        if not password:
            QMessageBox.warning(self, "خطا", "رمز عبور نمی‌تواند خالی باشد.")
            return

        if not master_exists():
            # ثبت رمز اولیه
            save_master_password(password)
            QMessageBox.information(
                self,
                "رمز ثبت شد",
                "رمز اصلی با موفقیت ثبت شد. از این پس برای ورود از همین رمز استفاده کنید.",
            )
            QMessageBox.information(self, "ورود موفق", "خوش آمدید! ✅")
            set_current_password(password)
            self.goto_main_window()

        elif check_master_password(password):
            set_current_password(password)
            self.goto_main_window()
        else:
            QMessageBox.critical(self, "خطای ورود", "رمز عبور نادرست است.")

    def goto_main_window(self):
        # در اینجا بعداً پنجره اصلی مدیریت رمزها لود می‌شه
        self.close()  # فعلاً فقط برنامه رو می‌بنده

    def goto_main_window(self):
        from main_window import MainWindow

        self.main_window = MainWindow()
        self.main_window.show()
        self.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    load_vazirmatn_font()
    window = LoginWindow()
    window.show()
    sys.exit(app.exec())
