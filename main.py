import sys
import sqlite3
from PyQt6 import uic
from PyQt6.QtWidgets import QApplication, QWidget, QTableWidgetItem


class Window(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi("main.ui", self)

        con = sqlite3.connect("coffee.sqlite")
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


app = QApplication(sys.argv)
w = Window()
w.show()
sys.exit(app.exec())
