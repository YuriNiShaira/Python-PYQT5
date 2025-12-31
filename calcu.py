import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QPushButton, QGridLayout
from PyQt5.QtGui import QIcon

class Widget(QWidget):
    def __init__(self):
        super().__init__()
        self.current_expression = "" 
        self.initUI()
        self.setWindowIcon(QIcon("profile.jpg"))

    def initUI(self):
        vbox = QVBoxLayout()

        # Display label
        self.label = QLabel("0", self)
        self.label.setStyleSheet("font-size: 24px; padding: 10px;")
        vbox.addWidget(self.label)

        # Grid layout for buttons
        grid = QGridLayout()
        self.buttons = [
            QPushButton("7"), QPushButton("8"), QPushButton("9"), QPushButton("/"),
            QPushButton("4"), QPushButton("5"), QPushButton("6"), QPushButton("*"),
            QPushButton("1"), QPushButton("2"), QPushButton("3"), QPushButton("-"),
            QPushButton("0"), QPushButton("C"), QPushButton("+"), QPushButton("="),
            QPushButton(".")
        ]

        # Button positions
        positions = [(0, 0), (0, 1), (0, 2), (0, 3),
                     (1, 0), (1, 1), (1, 2), (1, 3),
                     (2, 0), (2, 1), (2, 2), (2, 3),
                     (3, 0), (3, 1), (3, 2), (3, 3),
                     (4, 0)]

        for pos, btn in zip(positions, self.buttons):
            grid.addWidget(btn, *pos)
            btn.clicked.connect(self.buttonClicked)

        vbox.addLayout(grid)
        self.setLayout(vbox)
        self.setWindowTitle("Basic Calcu ni Shaira")
        self.resize(300, 200)
        self.setStyleSheet("""
                QPushButton {
                    font-size: 20px;
                    background-color: hsl(308, 100%, 76.3%);
                    color: white;
                    padding: 5px;
                    border-radius: 10px;
                }
                QPushButton:hover {
                    background-color: hsl(308, 100%, 65.3%);
                }
                QPushButton:pressed {
                    background-color: hsl(308, 100%, 25.3%);
                }
                QLabel {
                    font-size: 24px;
                    padding: 10px;
                    background-color: white;
                    border: 5px double black;
                }
        """)

    def buttonClicked(self):
        button = self.sender()
        text = button.text()

        if text == "C":
            self.current_expression = ""
            self.label.setText("0")
        elif text == "=":
            if self.current_expression == "143":  # Special case for "143"
                self.label.setText("I love Shaira")
                self.current_expression = ""  # Clear the expression
            elif self.current_expression == "5254":
                self.label.setText("Mahal na Mahal ko si Shaira Danica")
                self.current_expression = ""
            else:
                try:
                    result = eval(self.current_expression)
                    self.label.setText(str(result))
                    self.current_expression = str(result)
                except Exception:
                    self.label.setText("Error")
                    self.current_expression = ""
        else:
            self.current_expression += text
            self.label.setText(self.current_expression)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = Widget()
    widget.show()
    sys.exit(app.exec_())
