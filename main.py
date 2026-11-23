import sys
import sqlite3
from PyQt6.QtWidgets import QApplication, QWidget, QTableWidget, QTableWidgetItem
import os
from UI.main_ui import Ui_Form
from UI.addEditCoffeeForm_ui import Ui_AddEditCoffeeForm

if getattr(sys, "frozen", False):
    base = os.path.dirname(sys.executable)
else:
    base = os.path.dirname(os.path.abspath(__file__))

DB_PATH = os.path.join(base, "data", "coffee.sqlite")


class Window(QWidget, Ui_Form):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.tableWidget.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tableWidget.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.tableWidget.itemSelectionChanged.connect(self.on_select)
        self.addBtn.clicked.connect(self.add_coffee)
        self.editBtn.clicked.connect(self.edit_coffee)
        self.load_data()

    def load_data(self):
        con = sqlite3.connect(DB_PATH)
        cur = con.cursor()
        result = cur.execute("""
        SELECT coffee_info.id, name, roastings.roasting, types.type_name, description, cost, volume 
        FROM coffee_info
        JOIN roastings ON coffee_info.roasting = roastings.id
        JOIN types ON coffee_info.type = types.id
        """).fetchall()
        con.close()

        titles = ["ID", "Название", "Обжарка", "Тип", "Описание", "Цена", "Объём"]
        self.tableWidget.setColumnCount(len(titles))
        self.tableWidget.setHorizontalHeaderLabels(titles)
        self.tableWidget.setRowCount(len(result))

        for i, row in enumerate(result):
            for j, value in enumerate(row):
                self.tableWidget.setItem(i, j, QTableWidgetItem(str(value)))

        self.tableWidget.resizeColumnsToContents()

    def on_select(self):
        self.editBtn.setEnabled(bool(self.tableWidget.selectedItems()))

    def add_coffee(self):
        self.form = AddEditForm(self)
        self.form.show()

    def edit_coffee(self):
        row = self.tableWidget.currentRow()
        coffee_id = int(self.tableWidget.item(row, 0).text())
        self.form = AddEditForm(self, coffee_id)
        self.form.show()


class AddEditForm(QWidget, Ui_AddEditCoffeeForm):
    def __init__(self, parent, coffee_id=None):
        super().__init__()
        self.setupUi(self)

        self.parent_window = parent
        self.coffee_id = coffee_id
        if coffee_id is None:
            self.setWindowTitle("Добавить сорт кофе")
        else:
            self.setWindowTitle("Изменить сорт кофе")

        con = sqlite3.connect(DB_PATH)
        cur = con.cursor()

        roast_combo = cur.execute("""
                    SELECT id, roasting
                    FROM roastings
                    """).fetchall()
        for roast_id, text in roast_combo:
            self.roastingBox.addItem(text, roast_id)

        types_combo = cur.execute("""
                        SELECT id, type_name
                        FROM types
                        """).fetchall()
        for type_id, text in types_combo:
            self.typeBox.addItem(text, type_id)

        if coffee_id is not None:
            tpl = cur.execute(
                """
                        SELECT name, roasting, type, description, cost, volume
                        FROM coffee_info
                        WHERE id = ?
                        """,
                (coffee_id,),
            ).fetchone()
            name, roast, type_coffee, desc, cost, vol = tpl
            self.nameEdit.setText(name)
            self.roastingBox.setCurrentIndex(self.roastingBox.findData(roast))
            self.typeBox.setCurrentIndex(self.typeBox.findData(type_coffee))
            self.descEdit.setPlainText(desc)
            self.costBox.setValue(cost)
            self.volumeBox.setValue(vol)

        con.close()
        self.saveBtn.clicked.connect(self.save)

    def save(self):
        name = self.nameEdit.text()
        roast = self.roastingBox.currentData()
        type_id = self.typeBox.currentData()
        desc = self.descEdit.toPlainText()
        cost = self.costBox.value()
        volume = self.volumeBox.value()

        con = sqlite3.connect(DB_PATH)
        cur = con.cursor()

        if self.coffee_id is None:
            cur.execute(
                """
                INSERT INTO coffee_info (name, roasting, type, description, cost, volume)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (name, roast, type_id, desc, cost, volume),
            )
        else:
            cur.execute(
                """
                UPDATE coffee_info SET name = ?, roasting = ?, type = ?, 
                description = ?, cost = ?, volume = ? WHERE id = ?
                """,
                (name, roast, type_id, desc, cost, volume, self.coffee_id),
            )
        con.commit()
        con.close()

        self.parent_window.load_data()
        self.close()


app = QApplication(sys.argv)
w = Window()
w.show()
sys.exit(app.exec())
