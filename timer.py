import sys
import ctypes  
from PyQt5.QtWidgets import QMainWindow, QLabel, QMessageBox, QPushButton, QApplication, QDesktopWidget
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import QTimer, Qt, pyqtSignal
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

def resource_path(relative_path):
    """ Get the absolute path to the resource, works for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

from PyQt5.QtCore import pyqtSignal

class TimerWindow(QMainWindow):
    timer_closed = pyqtSignal()

    def __init__(self, email, student_number, remaining_time):
        super().__init__()

        self.resize(350, 150)
        self.setWindowTitle("Open Lab Timer")
        self.setWindowIcon(QIcon("logo.png"))
        self.setToolTip("OpenLab")

        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)

        self.move_to_lower_right()

        self.set_background_image("b2.png")

        # Use the remaining time passed from the login process
        self.time_remaining = remaining_time  
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_label)
        self.timer.start(1000)  # Update every second 

        self.label = QLabel(self)
        self.label.setGeometry(20, 60, 310, 50)
        self.label.setText(self.format_time(self.time_remaining))
        self.label.setStyleSheet("font-size: 20px; color: black; background: none; font-family: Arial; font-weight: bold;")

        self.email_label = QLabel(self)
        self.email_label.setGeometry(20, 10, 310, 20)
        self.email_label.setText(f"Email: {email}")
        self.email_label.setStyleSheet("font-size: 12px; color: black; background: none; font-family: Arial;")

        self.student_number_label = QLabel(self)
        self.student_number_label.setGeometry(20, 30, 310, 20)
        self.student_number_label.setText(f"Student Number: {student_number}")
        self.student_number_label.setStyleSheet("font-size: 12px; color: black; background: none; font-family: Arial;")

        self.login_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  
        self.login_time_label = QLabel(self)
        self.login_time_label.setGeometry(20, 50, 310, 20)
        self.login_time_label.setText(f"Logged In: {self.login_time}")
        self.login_time_label.setStyleSheet("font-size: 12px; color: black; background: none; font-family: Arial;")

        self.logout_button = QPushButton("Logout", self)
        self.logout_button.setGeometry(125, 100, 100, 30)
        self.logout_button.clicked.connect(self.logout)
        self.logout_button.setStyleSheet("background: #007bff; color: white; font-family: Arial; border: none; border-radius: 5px;")

        self.notified_30_minutes = False
        self.notified_2_minutes = False
        self.msg_box = None

    def closeEvent(self, event):
        """Override the closeEvent to emit a signal and allow main window to reopen.""" 
        self.timer_closed.emit()  
        event.accept()  

    def set_background_image(self, image_path):
        """Sets a background image for the window.""" 
        image_path = resource_path(image_path)  
        self.background_label = QLabel(self)
        self.background_label.setGeometry(0, 0, 350, 150)  
        self.background_label.setPixmap(QPixmap(image_path))
        self.background_label.setScaledContents(True)  

    def move_to_lower_right(self):
        """Moves the window to the lower-right corner of the screen with a 20px gap from the right edge.""" 
        desktop = QDesktopWidget()
        screen_rect = desktop.availableGeometry(desktop.primaryScreen())
        screen_width = screen_rect.width()
        screen_height = screen_rect.height()

        window_width = self.width()
        window_height = self.height()

        x_position = screen_width - window_width - 20
        y_position = screen_height - window_height - 20

        self.move(x_position, y_position)

    def format_time(self, seconds):
        hours, remainder = divmod(seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    def update_label(self):
        if self.time_remaining > 0:
            self.time_remaining -= 1
            self.label.setText(self.format_time(self.time_remaining))

            if self.time_remaining <= 300:
                self.label.setStyleSheet("font-size: 20px; color: red; background: none; font-family: Arial; font-weight: bold;")
            else:
                self.label.setStyleSheet("font-size: 20px; color: black; background: none; font-family: Arial; font-weight: bold;")

            if self.time_remaining == 1800 and not self.notified_30_minutes:
                self.notify_30_minutes_left()
                self.notified_30_minutes = True

            if self.time_remaining == 120 and not self.notified_2_minutes:
                self.notify_2_minutes_left()
                self.notified_2_minutes = True

        else:
        # Automatically log out when time runs out
            self.timer.stop()
            self.label.setText("Time's up!")
            self.logout()  # Call the logout function when time runs out

    def notify_30_minutes_left(self):
        self.msg_box = QMessageBox()
        self.msg_box.setIcon(QMessageBox.Information)
        self.msg_box.setWindowTitle("Time Alert")
        self.msg_box.setText("30 minutes remaining!")
        self.msg_box.setStandardButtons(QMessageBox.Ok)
        self.msg_box.show()

    def notify_2_minutes_left(self):
        """Notify the user that there are only 2 minutes left.""" 
        self.msg_box = QMessageBox()
        self.msg_box.setIcon(QMessageBox.Warning)
        self.msg_box.setWindowTitle("Time Alert")
        self.msg_box.setText("You only have 2 minutes remaining! Save your work!")
        self.msg_box.setStandardButtons(QMessageBox.Ok)
        self.msg_box.show()

    def lock_pc(self):
        """Locks the PC (Windows) when the timer ends."""
        # Lock the workstation
        ctypes.windll.user32.LockWorkStation()
        self.close()

    def logout(self):
        reply = QMessageBox.question(self, 'Logout Confirmation',
                                 "Are you sure you want to log out? Your remaining time will be saved.",
                                 QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            remaining_time_str = self.format_time(self.time_remaining)
            logout_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Update MongoDB with remaining time and logout time
            collection = connect_to_mongo()
            collection.update_one(
                {"email": self.email_label.text().replace("Email: ", ""), "student_number": self.student_number_label.text().replace("Student Number: ", "")},
                {"$set": {
                    "remaining_time": remaining_time_str,  # Store the updated remaining time
                    "logout_time": logout_time  # Store the logout time
                }}
            )

            msg_box = QMessageBox()
            msg_box.setIcon(QMessageBox.Information)
            msg_box.setWindowTitle("TIP Q.C. Claim ID")
            msg_box.setText("Thank you for using OpenLab. Claim your ID at ITSO.")
            msg_box.setStandardButtons(QMessageBox.Ok)

            screen_geometry = QDesktopWidget().availableGeometry().center()
            msg_box.setGeometry(screen_geometry.x() - 150, screen_geometry.y() - 50, 300, 100)

            msg_box.exec_()

            os.system('rundll32.exe user32.dll,LockWorkStation')  # Lock PC on Windows

            self.close()


def start_timer(email, student_number, remaining_time):
    """Creates the timer window and shows it with the given remaining time."""
    timer_window = TimerWindow(email, student_number, remaining_time)
    timer_window.show()
    return timer_window

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = start_timer("student@tip.edu.ph", "1234567")
    sys.exit(app.exec_())
