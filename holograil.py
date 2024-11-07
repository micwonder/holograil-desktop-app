import sys
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QLabel,
    QVBoxLayout,
    QWidget,
    QLineEdit,
    QPushButton,
    QFileDialog,
    QSpinBox,
    QMessageBox,
    QButtonGroup,
    QSpacerItem,
    QSizePolicy,
)
from PyQt5.QtGui import QColor, QIcon, QFont, QMovie
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import (
    QPalette,
    QDragEnterEvent,
    QDropEvent,
    QLinearGradient,
    QPalette,
    QLinearGradient,
    QColor,
    QBrush,
    QPixmap,
)
from PIL import Image, ImageSequence
import sys
import time
from datetime import datetime
from PyQt5.QtWidgets import (
    QDialog,
    QLabel,
    QVBoxLayout,
    QLineEdit,
    QPushButton,
    QApplication,
    QHBoxLayout,
    QFrame,
)
import shutil

import asyncio
from winotify import Notification, audio
from getmac import get_mac_address

import requests


class NumberOfCopiesDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Holograil")
        self.setFixedSize(350, 160)
        self.setStyleSheet("background-color:white; border: 0px")

        # Add the instruction label
        self.instructions_label = QLabel("Number of copies of image to be saved:", self)
        self.instructions_label.setAlignment(Qt.AlignCenter)
        self.instructions_label.setStyleSheet(
            """
                QLabel{
                    font-size: 15px;
                    font-family: 'Arial';
                }
            """
        )
        self.instructions_label.setGeometry(10, 15, 340, 40)

        # Add the copynumber input field (using QSpinBox now)
        self.copies_input = QSpinBox(self)
        self.copies_input.setValue(1)
        self.copies_input.setRange(1, 100)  # Set the range of the spin box
        self.copies_input.setFixedHeight(25)
        self.copies_input.setStyleSheet(
            """
                QSpinBox {
                    border: 2px solid black;
                    padding-left: 10px;
                    padding-right: 10px;
                }
                QSpinBox:focus {
                    border: 2px solid rgb(238, 183, 58);
                }
            """
        )
        self.copies_input.setGeometry(20, 60, 310, 30)

        # Add the okay button
        self.ok_button = QPushButton("OK", self)
        self.ok_button.clicked.connect(self.accept)
        self.ok_button.setStyleSheet(
            """
                QPushButton
                {
                    color: white;
                    background-color: rgb(74, 119, 215);
                    border-radius: 1px;
                    font-size: 14px;
                }
            """
        )
        self.ok_button.setGeometry(260, 100, 50, 30)

        # Add the cancel button
        self.cancel_button = QPushButton("Cancel", self)
        self.cancel_button.clicked.connect(self.reject)
        self.cancel_button.setStyleSheet(
            """
                QPushButton
                {
                    color: black;
                    background-color: rgb(221, 221, 221);
                    border-radius: 1px;
                    font-size: 13px;
                }
            """
        )
        self.cancel_button.setGeometry(180, 100, 70, 30)

    def get_number_of_copies(self):
        try:
            return int(self.copies_input.text())
        except ValueError:
            return None


class ImageCountNumberComponent(QWidget):
    def __init__(self):
        super().__init__()
        self.num_copies = 1  # Default number of copies
        self.build_widgets()
        self.build_layout()

    def build_widgets(self):
        self.decrement_button = QPushButton(
            text="-", styleSheet="background-color:white;color:black"
        )
        self.decrement_button.setFixedSize(32, 32)
        self.num_copies_label = QLabel(str(self.num_copies))
        self.num_copies_label.setFixedSize(32, 32)
        self.increment_button = QPushButton(
            text="+", styleSheet="background-color:white;color:black"
        )
        self.increment_button.setFixedSize(32, 32)

    def build_layout(self):
        # Set the background color to white
        self.container = QFrame()
        self.container.setStyleSheet("background-color: white")

        # Connect to a method to handle decrement, increment
        self.decrement_button.clicked.connect(self.decrement_copies)
        self.increment_button.clicked.connect(self.increment_copies)

        # Create a horizontal layout
        hbox_layout = QHBoxLayout(self.container)

        # Add the buttons and label to the layout
        hbox_layout.addSpacerItem(
            QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum)
        )
        hbox_layout.addWidget(self.decrement_button)
        hbox_layout.addWidget(self.num_copies_label)
        hbox_layout.addWidget(self.increment_button)
        hbox_layout.addSpacerItem(
            QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum)
        )
        hbox_layout.setContentsMargins(0, 0, 0, 0)  # Remove margins
        hbox_layout.setSpacing(0)

        lay = QVBoxLayout(self)
        lay.addWidget(self.container)

    def decrement_copies(self):
        if self.num_copies > 1:  # Ensure the number of copies does not go below 1
            self.num_copies -= 1
            self.num_copies_label.setText(
                str(self.num_copies)
            )  # Update the label to reflect the new number

    def increment_copies(self):
        self.num_copies += 1  # Increment the number of copies
        self.num_copies_label.setText(
            str(self.num_copies)
        )  # Update the label to reflect the new number


class DropArea(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.gif_movie = QMovie(None)
        self.folder = "D:\\"  # Default self.folder path
        self.processed_image = None
        self.num_frames = 1

        self.setAcceptDrops(True)
        self.setFixedSize(600, 600)

        # Create the main layout for the DropArea
        main_layout = QVBoxLayout(self)

        # 1st Layout: JPEG and GIF buttons
        button_layout = QHBoxLayout()
        self.jpg_button = QPushButton("JPEG", self)
        self.gif_button = QPushButton("GIF", self)

        # Create a button group to manage the selection
        self.button_group = QButtonGroup(self)  # Create a button group
        self.button_group.addButton(self.jpg_button)  # Add JPEG button to the group
        self.button_group.addButton(self.gif_button)  # Add GIF button to the group

        # Connect button clicked signals to update styles
        self.jpg_button.clicked.connect(lambda: self.update_button_styles("JPEG"))
        self.gif_button.clicked.connect(lambda: self.update_button_styles("GIF"))

        button_layout.addWidget(self.jpg_button)
        button_layout.addWidget(self.gif_button)
        main_layout.addLayout(button_layout)  # Add the button layout to the main layout

        ### ImageCountNumberComponent

        # Add the additional button layout to the main layout
        main_layout.addWidget(
            ImageCountNumberComponent()
        )  # Add the additional button layout to the main layout

        # 3rd Layout: Drag and drop area
        self.label = QLabel(
            f"""
            Drag and drop 2-3 JPEGs to be processed here.<br><br>
            Processed Image will be saved in: <br><br>
            <a href="desktop_path">{self.folder}</a>
            """,
            self,
        )

        # Set the initial selection to JPEG
        self.update_button_styles(
            "JPEG"
        )  # Update styles to reflect the initial selection

        self.label.setOpenExternalLinks(False)  # Prevent default link behavior
        self.label.setTextInteractionFlags(
            Qt.TextBrowserInteraction
        )  # Enable text interaction
        self.label.linkActivated.connect(self.handle_link_activated)

        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet(
            """
                QLabel {
                    background-color: rgba(238, 183, 58, 0);
                    font-family: 'Arial';
                    font-size: 20px;
                    border: 2px dashed white;
                    border-radius: 10px
                }
            """
        )
        main_layout.addWidget(self.label)  # Add the label to the main layout

        self.setLayout(main_layout)  # Set the main layout for the DropArea

    def update_button_styles(self, selected_button):
        if selected_button == "JPEG":
            self.is_jpg = True

        else:
            self.is_jpg = False

        # Reset styles for both buttons
        self.jpg_button.setStyleSheet(
            """
            QPushButton {
                background-color: #032061;  /* Unselected color */
                color: white;
                border: none;  /* Remove all borders */
                border-bottom: 2px solid white;  /* Add only bottom border */
                border-radius: 8px;  /* Remove border radius if you want sharp corners */
                font-weight: bold;
                height: 32px;
            }
            """
        )
        self.gif_button.setStyleSheet(
            """
            QPushButton {
                background-color: #032061;  /* Unselected color */
                color: white;
                border: none;  /* Remove all borders */
                border-bottom: 2px solid white;  /* Add only bottom border */
                border-radius: 8px;  /* Remove border radius if you want sharp corners */
                font-weight: bold;
                height: 32px;
            }
            """
        )

        # Apply selected style if the button is checked
        if self.is_jpg:
            self.jpg_button.setStyleSheet(
                """
                QPushButton {
                    background-color: #0372CD;  /* Selected color */
                    color: white;
                    border-bottom: 2px solid white;  /* Add only bottom border */
                    border-radius: 8px;
                    font-weight: bold;
                    height: 32px;
                }
                """
            )
            # Update label content for JPEG
            self.label.setText(
                f"""
                Drag and drop 2-3 JPEGs to be processed here.<br><br>
                Processed Image will be saved in: <br><br>
                <a href="desktop_path">{self.folder}</a>
                """
            )
        else:
            self.gif_button.setStyleSheet(
                """
                QPushButton {
                    background-color: #0372CD;  /* Selected color */
                    color: white;
                    border-bottom: 2px solid white;  /* Add only bottom border */
                    border-radius: 8px;
                    font-weight: bold;
                    height: 32px;
                }
                """
            )
            # Update label content for GIF
            self.label.setText(
                f"""
                Drag and drop GIFs to be processed here.<br><br>
                Processed Image will be saved in: <br><br>
                <a href="desktop_path">{self.folder}</a>
                """
            )

    def handle_link_activated(self, link):
        if link == "process_image":
            dialog = NumberOfCopiesDialog(self)
            if dialog.exec_() == QDialog.Accepted:
                self.num_copies = dialog.get_number_of_copies()
                if self.num_copies is not None:
                    print(f"Number of copies to save: {self.num_copies}")
                else:
                    self.num_copies = 1
                    print("Invalid number of copies")
        elif link == "desktop_path":
            self.folder = QFileDialog.getExistingDirectory(
                self, "Select Directory", self.folder
            )
            if self.folder:
                print(f"Selected directory: {self.folder}")
            else:
                self.folder = "D:\\"

        copy_text = "copy" if self.num_copies == 1 else "copies"
        self.label.setText(
            f"""
            Drag and drop GIF image to be processed here.<br><br>
            <a href="process_image">{self.num_copies} {copy_text}</a> of processed image will be saved in:<br><br>
            <a href="desktop_path">{self.folder}</a>
            """
        )

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            url = event.mimeData().urls()[0]
            if url.toLocalFile().lower().endswith(
                ".gif"
            ) or url.toLocalFile().lower().endswith(".jpg"):
                event.acceptProposedAction()
                self.label.setStyleSheet(
                    f"background-color: white; border: 2px dashed dimgray; border-radius: 10px; font-family: 'Arial'; font-size: 20px;"
                )
                return
        # self.label.setStyleSheet(f"background-color: {QColor(238, 183, 58).name()}; border: 2px dashed dimgray; border-radius: 10px")
        event.ignore()

    def dragLeaveEvent(self, event):
        self.label.setStyleSheet(
            f"background-color: {QColor(238, 183, 58).name()}; border: 2px dashed dimgray; border-radius: 10px; font-family: 'Arial'; font-size: 20px;"
        )

    def updateMovie(self, thread_obj, gif_path):
        self.gif_movie = QMovie(gif_path)
        self.gif_movie.setScaledSize(self.label.size())
        self.label.setMovie(self.gif_movie)
        self.gif_movie.start()

    def dropEvent(self, event: QDropEvent):
        file_paths = [url.toLocalFile() for url in event.mimeData().urls()]
        # self.processGif(files[0])
        # gif_path = file_paths[0]
        # self.updateMovie(gif_path)
        # process gif file
        num_copies = self.num_copies
        # For demo purposes, I'm setting some default values
        folder = self.folder
        # Get user parameters
        lpi = 40.07
        actual_lpi = 40
        width_in = 4
        height_in = 4
        resample_ppi = 600
        separator_ratio = 4
        separator_color = (150, 150, 150)

        # Get margins in inches
        top_margin_in = 0.25
        left_margin_in = 0.25
        right_margin_in = 0.25
        bottom_margin_in = 0.25

        # Start processing in a new thread
        self.processing_thread = GifProcessingThread(
            self.label,
            file_paths,
            num_copies,
            folder,
            lpi,
            actual_lpi,
            width_in,
            height_in,
            resample_ppi,
            separator_ratio,
            separator_color,
            top_margin_in,
            left_margin_in,
            right_margin_in,
            bottom_margin_in,
        )
        self.processing_thread.processing_finished.connect(self.on_processing_finished)
        self.processing_thread.update_movie.connect(self.updateMovie)
        self.processing_thread.start()

    def reset(self):
        # Stop any GIF animation
        if hasattr(self, "gif_movie") and self.gif_movie:
            self.gif_movie.stop()
            self.gif_movie = None
            delattr(self, "gif_movie")

        self.setAcceptDrops(True)
        self.label.setStyleSheet(
            f"background-color: {QColor(238, 183, 58).name()}; border: 2px dashed dimgray; border-radius: 10px; font-family: 'Arial'; font-size: 20px;"
        )
        # self.setFixedSize(460, 460)

        # Reset the label to its original state
        # self.label.clear()
        copy_text = "copy" if self.num_copies == 1 else "copies"
        self.label.setText(
            f"""
            Drag and drop GIF image to be processed here.<br><br>
            <a href="process_image">{self.num_copies} {copy_text}</a> of processed image will be saved in:<br><br>
            <a href="desktop_path">{self.folder}</a>
            """
        )

    def on_processing_finished(self, thread_obj, processing_time):
        if thread_obj.isRunning():
            thread_obj.quit()  # Forcefully stop the thread
            thread_obj.wait()  # Wait until the thread has completely finished

        if processing_time != 0:
            asyncio.run(
                self.show_notification(
                    "GIF Prcessing completed",
                    f"Processed image saved successfully (x{self.num_copies}). Time taken: {processing_time:.2f} seconds.",
                )
            )

        self.reset()

    async def show_notification(self, title, message):
        try:
            toast = Notification(
                app_id="Holograil GIF Image Processor",
                title=title,
                msg=message,
                duration="long",
                icon="C:\\ProgramData\\app_icon.ico",
            )
            toast.add_actions(
                label="Visit Holograil", launch="https://www.theholograil.com"
            )
            toast.set_audio(audio.Mail, loop=False)
            toast.show()
            # self.show_info_message(title, message)

        except Exception as e:
            self.show_error_message(str(e))

    def show_error_message(self, error_message):
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Critical)
        msg_box.setWindowTitle("Error")
        msg_box.setText("An error occurred:")
        msg_box.setInformativeText(error_message)
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec_()

    # def show_info_message(self, info_title, info_message):
    #     msg_box = QMessageBox()
    #     msg_box.setIcon(QMessageBox.Information)
    #     msg_box.setWindowTitle("Information")
    #     msg_box.setText(info_title)
    #     msg_box.setInformativeText(info_message)
    #     msg_box.exec_()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowIcon(QIcon("app_icon.ico"))

        self.setWindowTitle("TheGrail")
        self.setGeometry(100, 100, 800, 800)
        self.setFixedSize(800, 800)

        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Remove margins from main layout
        main_layout.setContentsMargins(0, 46, 0, 0)
        main_layout.setSpacing(30)

        # Create label for logo
        logo_label = QLabel()
        pixmap = QPixmap("./resources/logo.png")
        scaled_pixmap = pixmap.scaled(
            200, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation
        )
        logo_label.setPixmap(scaled_pixmap)
        logo_label.setAlignment(Qt.AlignCenter)

        # Add logo to layout
        main_layout.addWidget(logo_label)

        # After logo and before bottom images
        # Create center component
        center_widget = QWidget()
        self.meaning_area_widget = center_widget
        center_layout = QVBoxLayout(center_widget)

        # Create a container with background and border
        container = QWidget()
        container.setStyleSheet(
            """
            QWidget#container {
                background-color: rgba(88, 130, 193, 0.2);
                border-radius: 10px;
                border: 2px solid rgba(88, 130, 193, 0.2);
            }
        """
        )
        container.setObjectName("container")
        self.setStyleSheet(
            """
            * {
                font-family: 'Inter', sans-serif;
            }
            QLabel {
                color: white;
                font-size: 16px;
            }
            QPushButton {
                background-color: #15357D;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 5px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #4A6FA3;
            }
            QLineEdit {
                padding: 8px;
                border-radius: 5px;
                border: 1px solid rgba(255, 255, 255, 0.3);
                background: rgba(255, 255, 255, 0.1);
                color: white;
            }
        """
        )

        # Create container layout
        container_layout = QVBoxLayout(container)
        container_layout.setSpacing(15)
        container_layout.setContentsMargins(20, 20, 20, 20)

        # Add title label
        title_label = QLabel("Software must be activated")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; color: white;")
        container_layout.addWidget(title_label)

        # Add input fields
        from PyQt5.QtWidgets import QLineEdit

        # Username field
        xp_label_1 = QLabel(
            "You are using an unregistered version of the software. To activate the software, enter the license key."
        )
        xp_label_1.setStyleSheet("padding: 10px")
        xp_label_1.setWordWrap(True)
        xp_label_1.setFixedWidth(460)
        xp_label_4 = QLabel("Internet connection required during activation")
        xp_label_4.setStyleSheet("padding: 10px")
        xp_label_5 = QLabel("To get the key, copy the hardware ID and contact us")
        xp_label_5.setStyleSheet("padding: 10px")

        container_layout.addWidget(xp_label_1)
        container_layout.addWidget(xp_label_4)
        container_layout.addWidget(xp_label_5)

        # License key field
        key_label = QLabel("License Key:")
        key_label.setStyleSheet("font-weight: bold; color: white;")
        key_input = QLineEdit()
        key_input.setPlaceholderText("Enter your license key")
        self.license_key_input = key_input

        # Activate License Button
        activate_btn = QPushButton("Activate License")
        activate_btn.clicked.connect(self.click_next_button)

        hardward_label = QLabel("Hardware ID:")
        hardward_label.setStyleSheet("font-weight: bold; color: white;")
        mac_address = get_mac_address()
        hardward_id_label = QLabel(mac_address)

        # Copy ID button
        copy_btn = QPushButton("Copy ID")
        copy_btn.clicked.connect(self.copy_to_clipboard)

        container_layout.addWidget(key_label)
        container_layout.addWidget(key_input)

        container_layout.addWidget(activate_btn)
        container_layout.addWidget(hardward_label)
        container_layout.addWidget(hardward_id_label)
        container_layout.addWidget(copy_btn)

        # Set fixed size for container
        container.setFixedWidth(500)
        container.setFixedHeight(500)

        # Add container to center layout
        center_layout.addWidget(container, 0, Qt.AlignCenter)

        # Add center widget to main layout
        main_layout.addWidget(center_widget, 0, Qt.AlignCenter)

        # Create horizontal layout for bottom images
        bottom_layout = QHBoxLayout()

        # Left image
        left_label = QLabel()
        left_pixmap = QPixmap("./resources/left.png")
        scaled_left = left_pixmap.scaled(
            230, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation
        )
        left_label.setPixmap(scaled_left)

        # Right image
        right_label = QLabel()
        right_pixmap = QPixmap("./resources/right.png")
        scaled_right = right_pixmap.scaled(
            230, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation
        )
        right_label.setPixmap(scaled_right)

        # Add images to bottom layout
        bottom_layout.addWidget(left_label)
        bottom_layout.addStretch()  # Add space between images
        bottom_layout.addWidget(right_label)

        # Add spacer to push content to top and bottom
        main_layout.addStretch()

        # Add bottom layout to main layout
        main_layout.addLayout(bottom_layout)

        # Set up the gradient
        self.setup_linear_gradient()

        # Create the drop area, initially hidden
        self.drop_area = DropArea(self)
        self.drop_area.move(100, 140)
        self.drop_area.hide()

        self.setup_linear_gradient()

    def copy_to_clipboard(self):
        clipboard = QApplication.clipboard()
        clipboard.setText(get_mac_address())

    def setup_linear_gradient(self):
        gradient = QLinearGradient(0, 0, 0, self.height())
        gradient.setColorAt(0, QColor("#2B4099"))
        gradient.setColorAt(1, QColor("#89CAFF"))
        palette = self.create_gradient_palette(gradient)
        self.setPalette(palette)

    def click_next_button(self):
        if self.compare_license(self.license_key_input.text()):
            self.meaning_area_widget.hide()
            self.drop_area.show()

    def compare_license(self, input):
        mac_address = get_mac_address()
        url = "http://ec2-52-90-200-142.compute-1.amazonaws.com/subscriptions/validate-license"
        params = {
            "license_key": input,
            "device_address": mac_address,
        }
        response = requests.post(url, params=params)

        return True
        return response.status_code == 200

    def create_gradient_palette(self, gradient):
        palette = QPalette()
        brush = QBrush(gradient)
        palette.setBrush(QPalette.ColorRole.Window, brush)
        return palette


class GifProcessingThread(QThread):
    processing_finished = pyqtSignal(
        object, float
    )  # Signal to notify when processing is finished
    update_movie = pyqtSignal(object, str)

    def __init__(
        self,
        label,
        file_paths,
        num_copies,
        folder,
        lpi,
        actual_lpi,
        width_in,
        height_in,
        resample_ppi,
        separator_ratio,
        separator_color,
        top_margin_in,
        left_margin_in,
        right_margin_in,
        bottom_margin_in,
    ):
        super().__init__()
        self.label = label
        self.file_paths = file_paths
        self.num_copies = num_copies
        self.folder = folder
        self.lpi = lpi
        self.actual_lpi = actual_lpi
        self.width_in = width_in
        self.height_in = height_in
        self.resample_ppi = resample_ppi
        self.separator_ratio = separator_ratio
        self.separator_color = separator_color
        self.top_margin_in = top_margin_in
        self.left_margin_in = left_margin_in
        self.right_margin_in = right_margin_in
        self.bottom_margin_in = bottom_margin_in

    def run(self):
        try:
            start_time = time.time()

            if len(self.file_paths) == 1:
                if not self.file_paths[0].lower().endswith(".gif"):
                    self.processing_finished.emit(self, 0)
                    return
                else:
                    self.update_movie.emit(self, self.file_paths[0])
            else:
                for file_path in self.file_paths:
                    if file_path.lower().endswith(".gif"):
                        self.processing_finished.emit(self, 0)
                        return
                self.update_movie.emit(self, self.file_paths[0])

            print("Process Started")

            # Load GIF
            frames = []
            if len(self.file_paths) == 1:
                gif = Image.open(self.file_paths[0])
                frames = [frame.copy() for frame in ImageSequence.Iterator(gif)]
            else:
                for file_path in self.file_paths:
                    with Image.open(file_path) as img:
                        frames.append(img.copy())

            # Calculate resizing factor based on LPI deviation
            resize_factor = self.actual_lpi / self.lpi

            # Ensure margins are valid
            max_margin_width = min(self.width_in / 2, self.height_in / 2)
            if any(
                m > max_margin_width
                for m in [
                    self.top_margin_in,
                    self.left_margin_in,
                    self.right_margin_in,
                    self.bottom_margin_in,
                ]
            ):
                return

            # Calculate the new width and height including margins
            new_width_in = self.width_in + self.left_margin_in + self.right_margin_in
            new_height_in = self.height_in + self.top_margin_in + self.bottom_margin_in

            # Calculate pixel dimensions
            new_width_px = int(new_width_in * self.resample_ppi)
            new_height_px = int(new_height_in * self.resample_ppi * resize_factor)

            # Calculate the position to place the interlaced image (inside the margins)
            left_offset_px = int(self.left_margin_in * self.resample_ppi)
            top_offset_px = int(self.top_margin_in * self.resample_ppi)

            # Resize frames to fit within the area excluding the margins and considering LPI adjustment
            interlaced_area_width_px = int(self.width_in * self.resample_ppi)
            interlaced_area_height_px = int(
                self.height_in * self.resample_ppi * resize_factor
            )

            # Create a blank image with the new size
            interlaced_image = Image.new(
                "RGB", (new_width_px, new_height_px), (255, 255, 255)
            )  # White background for margins

            # tmp_time = time.time()
            # print(f"Till before step 1 {tmp_time - start_time}seconds elapsed")

            # --- Step 1: Add the Mark ---
            # Scale up by number of frames to make the mark height an integer
            # mark_scale_factor = len(frames) * 4
            mark_scale_factor = 4 if len(frames) == 3 else 2
            scaled_new_width_px = new_width_px * mark_scale_factor
            scaled_new_height_px = new_height_px * mark_scale_factor
            scaled_interlaced_image = interlaced_image.resize(
                (scaled_new_width_px, scaled_new_height_px), Image.LANCZOS
            )

            # Calculate stripe height and mark height
            stripe_height = int(
                (1 / self.actual_lpi)
                * self.resample_ppi
                / len(frames)
                * mark_scale_factor
            )
            mark_height = int(len(frames) * stripe_height / 2)

            # Add the stripe on the scaled image
            y_offset = int(
                (top_offset_px * mark_scale_factor + (len(frames) * stripe_height / 4))
            ) % (stripe_height * len(frames))
            for y in range(y_offset, scaled_new_height_px, len(frames) * stripe_height):
                mark_img = Image.new(
                    "RGB", (scaled_new_width_px, mark_height), (0, 0, 0)
                )
                scaled_interlaced_image.paste(mark_img, (0, y))

            # Scale back down to the original size
            interlaced_image = scaled_interlaced_image.resize(
                (new_width_px, new_height_px), Image.LANCZOS
            )

            # print(f"Step 1 spent {time.time() - tmp_time}seconds")
            # tmp_time = time.time()

            # --- Step 2: Interlace the Frames ---
            # Scale up by 2 to ensure the stripe height for interlacing is an integer
            # interlace_scale_factor = len(frames)
            interlace_scale_factor = 1 if len(frames) == 3 else 2
            scaled_interlaced_area_width_px = (
                interlaced_area_width_px * interlace_scale_factor
            )
            scaled_interlaced_area_height_px = (
                interlaced_area_height_px * interlace_scale_factor
            )
            scaled_interlaced_image = interlaced_image.resize(
                (
                    new_width_px * interlace_scale_factor,
                    new_height_px * interlace_scale_factor,
                ),
                Image.LANCZOS,
            )

            stripe_height = int(
                (1 / self.actual_lpi)
                * self.resample_ppi
                / len(frames)
                * interlace_scale_factor
            )

            interlace_offset = 0
            for i, frame in enumerate(frames):
                frame_resized = frame.resize(
                    (scaled_interlaced_area_width_px, scaled_interlaced_area_height_px),
                    Image.LANCZOS,
                )

                for y in range(
                    0, scaled_interlaced_area_height_px, len(frames) * stripe_height
                ):
                    scaled_interlaced_image.paste(
                        frame_resized.crop(
                            (0, y, scaled_interlaced_area_width_px, y + stripe_height)
                        ),
                        (
                            left_offset_px * interlace_scale_factor,
                            top_offset_px * interlace_scale_factor
                            + y
                            + i * stripe_height,
                        ),
                    )

            # Scale back down to the original size
            interlaced_image = scaled_interlaced_image.resize(
                (new_width_px, new_height_px), Image.LANCZOS
            )

            # print(f"Step 2 spent {time.time() - tmp_time}seconds")
            # tmp_time = time.time()

            # --- Step 3: Add Separators ---
            # Scale up by (separator_ratio + 1) to make the separator height an integer
            # separator_scale_factor = (self.separator_ratio + 1) * len(frames)
            separator_scale_factor = 1 if len(frames) == 3 else 2
            scaled_interlaced_area_width_px = (
                interlaced_area_width_px * separator_scale_factor
            )
            scaled_interlaced_area_height_px = (
                interlaced_area_height_px * separator_scale_factor
            )
            scaled_interlaced_image = interlaced_image.resize(
                (
                    new_width_px * separator_scale_factor,
                    new_height_px * separator_scale_factor,
                ),
                Image.LANCZOS,
            )

            stripe_height = int(
                (1 / self.actual_lpi)
                * self.resample_ppi
                / len(frames)
                * separator_scale_factor
            )
            separator_height = int(stripe_height / (self.separator_ratio + 1))

            # print(f"Step 3 spent {time.time() - tmp_time}seconds")
            # tmp_time = time.time()

            # Add separators (horizontal lines)
            for y in range(
                stripe_height - separator_height,
                scaled_interlaced_area_height_px,
                stripe_height,
            ):
                separator_img = Image.new(
                    "RGB",
                    (scaled_interlaced_area_width_px, separator_height),
                    self.separator_color,
                )
                scaled_interlaced_image.paste(
                    separator_img,
                    (
                        left_offset_px * separator_scale_factor,
                        top_offset_px * separator_scale_factor + y,
                    ),
                )

            # print(f"Add seperator step spent {time.time() - tmp_time}seconds")
            # tmp_time = time.time()

            # Scale back down to the original size
            interlaced_image = scaled_interlaced_image.resize(
                (new_width_px, new_height_px), Image.LANCZOS
            )

            # Resize after interlaced process
            resized_ratio = (new_width_px - 33 * 2) / (
                self.width_in * self.resample_ppi
            )
            new_size = (
                int(new_width_px * resized_ratio),
                int(new_height_px * resized_ratio),
            )

            img_resized = interlaced_image.resize(new_size, Image.LANCZOS)

            left = (img_resized.width - new_width_px) / 2
            top = (img_resized.height - new_height_px) / 2
            right = (img_resized.width + new_width_px) / 2
            bottom = (img_resized.height + new_height_px) / 2

            img_cropped = img_resized.crop((left, top, right, bottom))

            # print(f"Resize and crop step spent {time.time() - tmp_time}seconds")
            # tmp_time = time.time()

            now = datetime.now().strftime("%d_%m_%Y__%H_%M_%S")

            if self.num_copies == 1:
                img_cropped.save(
                    f"{self.folder}\\{len(frames)}frames_{now}.tiff",
                    format="TIFF",
                    dpi=(self.resample_ppi, self.resample_ppi),
                )
            elif self.num_copies > 1:
                for i in range(self.num_copies):
                    img_cropped.save(
                        f"{self.folder}\\{len(frames)}frames_{now}_{i + 1}.tiff",
                        format="TIFF",
                        dpi=(self.resample_ppi, self.resample_ppi),
                    )

            end_time = time.time()
            processing_time = end_time - start_time

            self.processing_finished.emit(self, processing_time)

        except Exception as e:
            self.show_error_message(str(e))

    def show_error_message(self, error_message):
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Critical)
        msg_box.setWindowTitle("Error")
        msg_box.setText("An error occurred:")
        msg_box.setInformativeText(error_message)
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec_()


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    shutil.copyfile("./app_icon.ico", "C:\\ProgramData\\app_icon.ico")
    main()
