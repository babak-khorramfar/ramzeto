from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QLabel,
    QCheckBox,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QSlider,
    QMessageBox,
    QSpacerItem,
    QSizePolicy,
    QAbstractItemView,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QGuiApplication
import string
import random
from core.auth import clear_current_password
import json
import os

DATA_FILE = "data.json"


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("رمزتو - مدیریت رمزها")
        self.setMinimumSize(980, 750)
        self.entries = []
        self.init_ui()

    def init_ui(self):
        self.load_entries()  # ← بارگذاری خودکار داده‌ها
        main_layout = QVBoxLayout(self)

        # # نوار منو
        # self.menu_bar = QMenuBar(self)
        # file_menu = self.menu_bar.addMenu("فایل")
        # exit_action = file_menu.addAction("خروج")
        # exit_action.triggered.connect(self.logout)
        # main_layout.setMenuBar(self.menu_bar)

        # عنوان بالا
        title_label = QLabel("🗂️ مدیریت رمزهای شما")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 20px; font-weight: bold; margin: 10px;")
        main_layout.addWidget(title_label)

        # جستجو
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search ...")
        self.search_bar.setAlignment(Qt.AlignRight)
        self.search_bar.textChanged.connect(self.filter_entries)
        self.search_bar.setFixedHeight(36)
        main_layout.addWidget(self.search_bar)

        # جدول
        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(
            ["Website", "Username", "Password", "More info1", "More info2"]
        )
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        main_layout.addWidget(self.table)

        # فیلدها
        field_layout = QHBoxLayout()
        self.input_site = self.create_input("Website")
        self.input_user = self.create_input("Username")
        self.input_pass = self.create_input("Password")
        self.input_note1 = self.create_input("More info1")
        self.input_note2 = self.create_input("More info2")
        field_layout.addWidget(self.input_site)
        field_layout.addWidget(self.input_user)
        field_layout.addWidget(self.input_pass)
        field_layout.addWidget(self.input_note1)
        field_layout.addWidget(self.input_note2)
        main_layout.addLayout(field_layout)

        # دکمه‌های افزودن و حذف
        btn_layout = QHBoxLayout()
        self.btn_add = QPushButton("➕ Add")
        self.btn_add.setMinimumHeight(36)
        self.btn_add.clicked.connect(self.add_entry)

        self.btn_delete = QPushButton("🗑 Delete Selected")
        self.btn_delete.setMinimumHeight(36)
        self.btn_delete.clicked.connect(self.delete_selected)

        btn_layout.addWidget(self.btn_add)
        btn_layout.addWidget(self.btn_delete)
        btn_layout.addItem(
            QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        )
        main_layout.addLayout(btn_layout)

        # ساخت رمز امن
        self.label_title = QLabel("🔐 ساخت رمز امن")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 20px; font-weight: bold; margin: 10px;")
        main_layout.addWidget(self.label_title)

        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMinimum(4)
        self.slider.setMaximum(32)
        self.slider.setValue(12)
        self.slider.valueChanged.connect(self.update_length_label)
        main_layout.addWidget(self.slider)

        self.label_length = QLabel("Password Leghnt: 12")
        self.label_length.setAlignment(Qt.AlignRight)
        main_layout.addWidget(self.label_length)

        self.chk_upper = QCheckBox("Capital (A-Z)")
        self.chk_digits = QCheckBox("Numbers (0-9)")
        self.chk_symbols = QCheckBox("Characters (!@#$...)")

        gen_layout = QHBoxLayout()
        gen_layout.setSpacing(15)
        gen_layout.addWidget(self.chk_upper)
        gen_layout.addWidget(self.chk_digits)
        gen_layout.addWidget(self.chk_symbols)
        main_layout.addLayout(gen_layout)

        self.btn_generate = QPushButton("🎲 Generate Password")
        self.btn_generate.setMinimumHeight(36)
        self.btn_generate.clicked.connect(self.generate_password)

        self.btn_copy = QPushButton("📋 Copy")
        self.btn_copy.setMinimumHeight(36)
        self.btn_copy.clicked.connect(self.copy_password)

        gen_btns = QHBoxLayout()
        gen_btns.addWidget(self.btn_generate)
        gen_btns.addWidget(self.btn_copy)
        main_layout.addLayout(gen_btns)

        # دکمه خروج از حساب
        self.btn_logout = QPushButton("🚪 Logout and Close")
        self.btn_logout.setMinimumHeight(36)
        self.btn_logout.clicked.connect(self.logout)
        main_layout.addWidget(self.btn_logout, alignment=Qt.AlignRight)

        self.load_entries()

    def create_input(self, placeholder):
        le = QLineEdit()
        le.setPlaceholderText(placeholder)
        le.setAlignment(Qt.AlignRight)
        le.setFixedHeight(36)
        return le

    def add_entry(self):
        data = [
            self.input_site.text().strip(),
            self.input_user.text().strip(),
            self.input_pass.text().strip(),
            self.input_note1.text().strip(),
            self.input_note2.text().strip(),
        ]
        if not all(data[:3]):
            QMessageBox.warning(
                self, "خطا", "پر کردن فیلدهای سایت، نام کاربری و رمز عبور الزامی است."
            )
            return
        self.entries.append(data)
        self.refresh_table()
        self.save_entries()  # ← بعد از افزودن یا حذف
        for field in [
            self.input_site,
            self.input_user,
            self.input_pass,
            self.input_note1,
            self.input_note2,
        ]:
            field.clear()

    def delete_selected(self):
        row = self.table.currentRow()
        if row >= 0:
            self.entries.pop(row)
            self.refresh_table()
            self.save_entries()  # ← بعد از افزودن یا حذف

    def refresh_table(self):
        self.table.setRowCount(0)
        for entry in self.entries:
            row = self.table.rowCount()
            self.table.insertRow(row)
            for col, value in enumerate(entry):
                self.table.setItem(row, col, QTableWidgetItem(value))
        self.filter_entries()

    def filter_entries(self):
        keyword = self.search_bar.text().lower()
        for i in range(self.table.rowCount()):
            match = keyword in self.table.item(i, 0).text().lower()
            self.table.setRowHidden(i, not match)

    def update_length_label(self, value):
        self.label_length.setText(f"طول: {value}")

    def generate_password(self):
        length = self.slider.value()
        charset = list(string.ascii_lowercase)
        if self.chk_upper.isChecked():
            charset += list(string.ascii_uppercase)
        if self.chk_digits.isChecked():
            charset += list(string.digits)
        if self.chk_symbols.isChecked():
            charset += list("!@#$%^&*()-_=+[]{}")
        if not charset:
            QMessageBox.warning(self, "خطا", "حداقل یک گزینه باید انتخاب شود.")
            return
        password = "".join(random.choice(charset) for _ in range(length))
        self.input_pass.setText(password)

    def copy_password(self):
        QGuiApplication.clipboard().setText(self.input_pass.text())

    def logout(self):
        clear_current_password()
        self.close()

    def save_entries(self):
        try:
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(self.entries, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print("خطا در ذخیره‌سازی:", e)

    def load_entries(self):
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, "r", encoding="utf-8") as f:
                    self.entries = json.load(f)
                    self.refresh_table()
            except Exception as e:
                print("خطا در بارگذاری:", e)
