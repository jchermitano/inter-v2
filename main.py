import sys
from PyQt5.QtWidgets import QInputDialog, QApplication, QMainWindow, QLineEdit, QPushButton, QMessageBox
from PyQt5.QtGui import QIcon, QIntValidator, QPixmap, QPalette, QBrush
from PyQt5.QtCore import Qt
from PyQt5 import QtCore
import re
import timer
from datetime import datetime
import os
import pymongo  # Add this import at the top with other imports

# Add your MongoDB connection details
MONGO_URI = "mongodb+srv://johnnyhermitano02:o3awZpQZJ5D7YMCr@itso.zngrn.mongodb.net/"  # Replace with your MongoDB URI
DB_NAME = "itsodb"    # Replace with your database name
COLLECTION_NAME = "logs"  # Replace with your collection name

# Function to connect to MongoDB
def connect_to_mongo():
    client = pymongo.MongoClient(MONGO_URI)
    db = client[DB_NAME]
    return db[COLLECTION_NAME]

def on_submit():
    email = name_input.text()
    student_number = student_number_input.text()

    # Perform validation for email and student number
    if not re.match(r'^[\w\.-]+@tip\.edu\.ph$', email):
        QMessageBox.warning(win, "Email Error", "Please enter a valid TIP email.")
        return

    if len(student_number) != 7:
        QMessageBox.warning(win, "Student Number Error", "Please enter a valid Student Number.")
        return

    # Connect to MongoDB
    collection = connect_to_mongo()
    current_time = datetime.now()
    current_date = current_time.strftime('%Y-%m-%d')

    # Retrieve user data from MongoDB for today's login
    user_data_today = collection.find_one({
        "email": email, 
        "student_number": student_number, 
        "login_date": current_date  # Ensure you're checking for the same date
    })

    if user_data_today:
        remaining_time = user_data_today.get("remaining_time", "02:00:00")  # Default 2 hours in 'HH:MM:SS' format

        # Convert the 'HH:MM:SS' time format to seconds
        if isinstance(remaining_time, str):
            hours, minutes, seconds = map(int, remaining_time.split(':'))
            remaining_time = hours * 3600 + minutes * 60 + seconds

        # Check if they have time left
        if remaining_time <= 0:
            QMessageBox.warning(win, "Session Error", "Your time for today is consumed. You cannot start a new session.")
            return
    else:
        # New login for today, insert a new document with 2 hours (7200 seconds)
        remaining_time = 7200
        collection.insert_one({
            "email": email,
            "student_number": student_number,
            "login_date": current_date,
            "remaining_time": remaining_time,
            "timestamp": current_time.strftime('%Y-%m-%d %I:%M:%S %p')  # Store login timestamp
        })

    # Clear input fields after successful login
    name_input.clear()
    student_number_input.clear()

    # Proceed to start the timer window
    win.hide()

    global timer_window
    timer_window = timer.start_timer(email, student_number, remaining_time)
    timer_window.timer_closed.connect(show_main_window)

def resource_path(relative_path):
    """ Get the absolute path to the resource, works for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

def show_main_window():
    """Function to show the main window when the timer window is closed.""" 
    win.show()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setGeometry(800, 300, 500, 500)
        self.setWindowTitle("Open Lab")
        self.setWindowIcon(QIcon("logo.png"))
        self.setToolTip("OpenLab")

        self.set_background("login.png")

        window_width = self.width()
        window_height = self.height()
        input_width = 300
        input_height = 40
        button_width = 150
        button_height = 40
        x_center = (window_width - input_width) // 2
        y_center = (window_height // 2) - 30  

        global name_input
        name_input = QLineEdit(self)
        name_input.setPlaceholderText("Enter your TIP Email")
        name_input.setGeometry(x_center, y_center, input_width, input_height)
        name_input.setStyleSheet("""
            border: 1px solid #C0C0C0;
            border-radius: 15px;
            padding: 5px;
            font-size: 14px;
            background: #FFFFFF;  /* Solid white background */
        """)

        global student_number_input
        student_number_input = QLineEdit(self)
        student_number_input.setPlaceholderText("Enter your Student Number")
        student_number_input.setGeometry(x_center, y_center + 60, input_width, input_height)
        student_number_input.setStyleSheet("""
            border: 1px solid #C0C0C0;
            border-radius: 15px;
            padding: 5px;
            font-size: 14px;
            background: #FFFFFF;  /* Solid white background */
        """)
        
        int_validator = QIntValidator(0, 9999999)
        student_number_input.setValidator(int_validator)

        login_button = QPushButton("Start Session", self)
        login_button.setGeometry((window_width - button_width) // 2, y_center + 130, button_width, button_height)
        login_button.setStyleSheet("""
            QPushButton {
                border: 2px solid #333;
                border-radius: 20px;
                background-color: #333; /* Black color */
                color: #FFF; /* White text color */
                font-size: 16px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #444; /* Slightly lighter black on hover */
            }
        """)
        login_button.clicked.connect(on_submit)
    
    def set_background(self, image_path):
        """Set background image of the window."""
        image_path = resource_path(image_path)  
        background = QPixmap(image_path)
        background = background.scaled(self.size(), QtCore.Qt.KeepAspectRatioByExpanding, QtCore.Qt.SmoothTransformation)
        palette = self.palette()
        palette.setBrush(QPalette.Window, QBrush(background))
        self.setPalette(palette)

    def closeEvent(self, event):
        """Override the closeEvent to require a password before closing."""
        password, ok = QInputDialog.getText(self, 'Admin Password', 'Enter password to close:', QLineEdit.Password)

        if ok and password == "123":  # Change this to the default password
            event.accept()  # Close the application if the password is correct
        else:
            QMessageBox.warning(self, "Incorrect Password", "The password you entered is incorrect.")
            event.ignore()  # Prevent closing if the password is incorrect

def window():
    app = QApplication(sys.argv)
    global win
    win = MainWindow()
    win.setWindowFlags(QtCore.Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
    win.show()
    sys.exit(app.exec_())

window()
