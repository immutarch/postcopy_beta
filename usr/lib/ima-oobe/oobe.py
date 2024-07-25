import sys
import subprocess
from threading import Thread
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QLineEdit, QPushButton,
    QComboBox, QStackedWidget, QFormLayout, QSizePolicy, QMessageBox, QPlainTextEdit
)
from PyQt5.QtCore import Qt, QProcess
from PyQt5.QtGui import QFont

class OOBEWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Out-of-box Experience")
        self.setGeometry(100, 100, 800, 600)
        self.selected_timezone = None  # Add this line

        # Disable close and maximize buttons
        self.setWindowFlags(Qt.Window | Qt.CustomizeWindowHint | Qt.WindowMinimizeButtonHint)

        # Main container for pages
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        # Define heading style
        self.heading_font = QFont()
        self.heading_font.setPointSize(18)
        self.heading_font.setBold(True)

        # Welcome page
        self.welcome_page = QWidget()
        self.welcome_layout = QVBoxLayout()

        # Heading for welcome page
        self.welcome_heading_label = QLabel("Welcome")
        self.welcome_heading_label.setFont(self.heading_font)
        self.welcome_heading_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        # Content layout
        self.welcome_content_layout = QVBoxLayout()
        self.welcome_label = QLabel("Welcome to the Immutarch Setup Wizard!")
        self.welcome_label.setAlignment(Qt.AlignCenter)
        font = QFont()
        font.setPointSize(24)
        font.setBold(True)
        self.welcome_label.setFont(font)

        self.next_button_welcome = QPushButton("Next")
        self.next_button_welcome.clicked.connect(self.show_timezone_page)

        # Add heading and content to the layout
        self.welcome_content_layout.addStretch()
        self.welcome_content_layout.addWidget(self.welcome_label, alignment=Qt.AlignCenter)
        self.welcome_content_layout.addStretch()
        self.welcome_content_layout.addWidget(self.next_button_welcome, alignment=Qt.AlignCenter)

        self.welcome_layout.addWidget(self.welcome_heading_label)
        self.welcome_layout.addLayout(self.welcome_content_layout)
        self.welcome_layout.setContentsMargins(20, 20, 20, 20)
        self.welcome_page.setLayout(self.welcome_layout)

        # Timezone selection page
        self.timezone_page = QWidget()
        self.timezone_layout = QVBoxLayout()

        # Heading for timezone page
        self.timezone_heading_label = QLabel("Timezone Selection")
        self.timezone_heading_label.setFont(self.heading_font)
        self.timezone_heading_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        # Content layout
        self.timezone_label = QLabel("Select Your Timezone")
        self.timezone_label.setAlignment(Qt.AlignCenter)
        self.timezone_combobox = QComboBox()
        self.timezone_combobox.addItems(self.get_timezones())
        self.next_button_timezone = QPushButton("Next")
        self.next_button_timezone.clicked.connect(self.show_user_page)

        # Previous button
        self.previous_button_timezone = QPushButton("Previous")
        self.previous_button_timezone.clicked.connect(self.show_welcome_page)

        # Add heading and content to the layout
        self.timezone_layout.addWidget(self.timezone_heading_label)
        self.timezone_layout.addStretch()
        self.timezone_layout.addWidget(self.timezone_label, alignment=Qt.AlignCenter)
        self.timezone_layout.addWidget(self.timezone_combobox, alignment=Qt.AlignCenter)
        self.timezone_layout.addStretch()
        self.timezone_layout.addWidget(self.previous_button_timezone, alignment=Qt.AlignLeft)
        self.timezone_layout.addWidget(self.next_button_timezone, alignment=Qt.AlignCenter)
        self.timezone_layout.setContentsMargins(20, 20, 20, 20)
        self.timezone_page.setLayout(self.timezone_layout)

        # User creation page
        self.user_page = QWidget()
        self.user_layout = QVBoxLayout()

        # Heading for user page
        self.user_heading_label = QLabel("User Creation")
        self.user_heading_label.setFont(self.heading_font)
        self.user_heading_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        self.form_layout = QFormLayout()

        self.username_label = QLabel("Username")
        self.username_input = QLineEdit()
        self.password_label = QLabel("Password")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.hostname_label = QLabel("Hostname for this installation")
        self.hostname_input = QLineEdit()
        self.root_password_label = QLabel("Root Password")
        self.root_password_input = QLineEdit()
        self.root_password_input.setEchoMode(QLineEdit.Password)
        self.finish_button = QPushButton("Finish")
        self.finish_button.clicked.connect(self.finish_setup)

        self.form_layout.addRow(self.username_label, self.username_input)
        self.form_layout.addRow(self.password_label, self.password_input)
        self.form_layout.addRow(self.hostname_label, self.hostname_input)
        self.form_layout.addRow(self.root_password_label, self.root_password_input)

        self.user_layout.addWidget(self.user_heading_label)
        self.user_layout.addStretch()
        self.user_layout.addLayout(self.form_layout)
        self.user_layout.addStretch()
        self.user_layout.addWidget(self.finish_button, alignment=Qt.AlignCenter)
        self.user_layout.setContentsMargins(20, 20, 20, 20)
        self.user_page.setLayout(self.user_layout)

        # Command output page
        self.command_output_page = QWidget()
        self.command_output_layout = QVBoxLayout()
        self.command_output_label = QLabel("Running setup command...")
        self.command_output_label.setAlignment(Qt.AlignCenter)
        self.command_output_text = QPlainTextEdit()
        self.command_output_text.setReadOnly(True)
        self.command_output_layout.addWidget(self.command_output_label)
        self.command_output_layout.addWidget(self.command_output_text)
        self.command_output_page.setLayout(self.command_output_layout)

        # Setup complete page
        self.setup_complete_page = QWidget()
        self.setup_complete_layout = QVBoxLayout()
        self.setup_complete_label = QLabel("Setup Complete!")
        self.setup_complete_label.setAlignment(Qt.AlignCenter)
        self.setup_complete_label.setFont(self.heading_font)

        # Finish button
        self.finish_button_complete = QPushButton("Finish")
        self.finish_button_complete.clicked.connect(self.close_application)

        self.setup_complete_layout.addWidget(self.setup_complete_label)
        self.setup_complete_layout.addWidget(self.finish_button_complete, alignment=Qt.AlignCenter)  # Add button to layout
        self.setup_complete_page.setLayout(self.setup_complete_layout)


        # Add pages to stacked widget
        self.stacked_widget.addWidget(self.welcome_page)
        self.stacked_widget.addWidget(self.timezone_page)
        self.stacked_widget.addWidget(self.user_page)
        self.stacked_widget.addWidget(self.command_output_page)
        self.stacked_widget.addWidget(self.setup_complete_page)

        # Center the window on the screen
        qr = self.frameGeometry()
        cp = QApplication.desktop().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def get_timezones(self):
        try:
            output = subprocess.check_output(['timedatectl', 'list-timezones'])
            timezones = output.decode('utf-8').strip().split('\n')
            return timezones
        except Exception as e:
            print(f"Error fetching timezones: {e}")
            return ["UTC"]  # Fallback timezone

    def show_welcome_page(self):
        self.stacked_widget.setCurrentWidget(self.welcome_page)

    def show_timezone_page(self):
        self.stacked_widget.setCurrentWidget(self.timezone_page)

    def show_user_page(self):
        self.selected_timezone = self.timezone_combobox.currentText()
        self.stacked_widget.setCurrentWidget(self.user_page)

    def validate_user_input(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()

        if not username or not password:
            # Show an alert if username or password is empty
            QMessageBox.warning(
                self,
                "Input Error",
                "Both username and password must be provided.",
                QMessageBox.Ok
            )
            return False
        return True

    def close_application(self):
        self.close()

    def finish_setup(self):
        if not self.validate_user_input():
            return  # Do not proceed if validation fails

        # Prepare the command
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        root_password = self.root_password_input.text().strip()
        hostname = self.hostname_input.text().strip()
        timezone = self.selected_timezone

        command = f"/usr/lib/ima-oobe/ima-oobe-finalize --tz \"{timezone}\" --username \"{username}\" --password \"{password}\""
        if hostname:
            command += f" --hostname \"{hostname}\""
        if root_password:
            command += f" --root_password \"{root_password}\""

        # Display command output page
        self.stacked_widget.setCurrentWidget(self.command_output_page)

        # Execute the command
        self.run_command(command)

    def run_command(self, command):
        self.process = QProcess(self)
        self.process.setProcessChannelMode(QProcess.MergedChannels)
        self.process.readyReadStandardOutput.connect(self.handle_stdout)
        self.process.readyReadStandardError.connect(self.handle_stderr)
        self.process.finished.connect(self.process_finished)
        self.process.start(command)

    def handle_stdout(self):
        data = self.process.readAllStandardOutput().data().decode()
        self.command_output_text.appendPlainText(data)

    def handle_stderr(self):
        data = self.process.readAllStandardError().data().decode()
        self.command_output_text.appendPlainText(data)

    def process_finished(self):
        self.command_output_text.appendPlainText("\nCommand execution finished.")
        self.switch_to_setup_complete_page()

    def switch_to_setup_complete_page(self):
        self.stacked_widget.setCurrentWidget(self.setup_complete_page)


app = QApplication(sys.argv)
window = OOBEWindow()
window.show()
sys.exit(app.exec_())
