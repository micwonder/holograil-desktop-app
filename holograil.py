import sys
import logging
import imghdr
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QLabel,
    QVBoxLayout,
    QWidget,
    QGridLayout,
    QPushButton,
    QFileDialog,
    QSpinBox,
    QMessageBox,
    QButtonGroup,
    QSpacerItem,
    QSizePolicy,
    QFrame,
)
from PyQt5.QtGui import QColor, QIcon, QFont, QMovie
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer, QSize
from PyQt5.QtGui import (
    QIntValidator,
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
)
import shutil

import asyncio
from winotify import Notification, audio
from getmac import get_mac_address

import requests

# Configure the logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s [Thread: %(threadName)s | ID: %(thread)d]",
)


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
        self.container.resize(100, 100)

    def build_widgets(self):
        self.decrement_button = QPushButton(text="-")
        self.decrement_button.setStyleSheet(
            """
                                            QPushButton {
                                                font-size: 32px;
                                                color: #2B4099;
                                                border: 1px solid #FFFFFF;
                                                border-radius: 8px;
                                                font-family: 'Arial';
                                            }
        """
        )
        # self.decrement_button.setFixedSize(32, 32)
        self.num_copies_input = QLineEdit(str(self.num_copies))
        self.num_copies_input.setStyleSheet(
            """
                                            QLineEdit {
                                                color: #2B4099;
                                                font-family: 'Arial';
                                                text-align: center;
                                                font-size: 16px;
                                            }
                                            """
        )
        # self.num_copies_input.setFixedSize(32, 32)
        self.num_copies_input.setAlignment(Qt.AlignCenter)
        self.increment_button = QPushButton(text="+")
        self.increment_button.setStyleSheet(
            """
                                            QPushButton {
                                                font-size: 20px;
                                                color: #2B4099;
                                                border-radius: 8px;
                                                font-family: 'Arial';
                                            }
        """
        )
        # self.increment_button.setFixedSize(32, 32)

    def build_layout(self):
        # Set the background color to white
        self.container = QFrame()
        self.container.setStyleSheet(
            "background-color: white; border-radius: 5px; color: black"
        )
        self.container.setMaximumWidth(200)

        # Connect to a method to handle decrement, increment
        self.decrement_button.clicked.connect(self.decrement_copies)
        self.increment_button.clicked.connect(self.increment_copies)
        self.num_copies_input.textChanged.connect(self.sync_with_label)
        onlyInt = QIntValidator()
        onlyInt.setRange(0, 99)
        self.num_copies_input.setValidator(onlyInt)

        # Create a horizontal layout
        hbox_layout = QHBoxLayout(self.container)

        # Add the buttons and label to the layout
        hbox_layout.addSpacerItem(
            QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum)
        )
        hbox_layout.addWidget(self.decrement_button)
        hbox_layout.addWidget(self.num_copies_input)
        hbox_layout.addWidget(self.increment_button)
        hbox_layout.addSpacerItem(
            QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum)
        )
        hbox_layout.setContentsMargins(0, 0, 0, 0)  # Remove margins
        hbox_layout.setSpacing(15)

        lay = QVBoxLayout(self)
        lay.addWidget(self.container, alignment=Qt.AlignCenter)
        self.container.setFixedHeight(self.container.sizeHint().height())

    def decrement_copies(self):
        if self.num_copies > 1:  # Ensure the number of copies does not go below 1
            self.num_copies -= 1
            self.update_display()

    def increment_copies(self):
        if self.num_copies < 99:
            self.num_copies += 1  # Increment the number of copies
            self.update_display()

    def update_display(self):
        self.num_copies_input.setText(str(self.num_copies))

    def sync_with_label(self):
        text = self.num_copies_input.text()
        value = int(text)
        if 0 <= value <= 99:
            self.num_copies = value


class ImagePanel(QWidget):
    def __init__(self, file_path, max_length=12):
        super().__init__()
        self.file_path = file_path
        self.content = self.truncate_content(file_path.split("/")[-1], max_length)
        self.build_widgets()
        self.build_layout()

    def truncate_content(self, content, max_length):
        if len(content) > max_length:
            return content[: max_length - 3] + "..."
        return content

    def build_widgets(self):
        self.content_label = QLabel(self.content)
        self.content_label.setFixedSize(110, 50)
        self.close_btn = QPushButton("X")
        self.close_btn.setFixedSize(20, 20)
        self.close_btn.clicked.connect(self.closePanel)

    def build_layout(self):
        self.container = QFrame()
        self.container.setStyleSheet(
            "background-color: #D9D9D9; border-radius: 5px; color: #595959;font-size: 12px; margin: 0; padding:0; border: none"
        )
        self.content_label.setStyleSheet("border: none")
        self.close_btn.setStyleSheet(
            "font-size:10px; padding:0; margin:0; border: none"
        )
        gridbox = QGridLayout(self.container)

        gridbox.addWidget(self.content_label, 0, 0, 2, 1)
        gridbox.addWidget(self.close_btn, 0, 1, 1, 1)
        gridbox.setSpacing(0)
        gridbox.setContentsMargins(0, 0, 0, 0)
        self.content_label.setAlignment(Qt.AlignCenter)

        lay = QHBoxLayout(self)
        lay.addStretch(1)
        lay.addWidget(self.container)
        self.container.setFixedHeight(self.container.sizeHint().height())
        self.setMaximumWidth(200)

    def closePanel(self):
        self.setParent(None)
        self.deleteLater()


class DropArea(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.gif_movie = QMovie(None)
        self.folder = "D:\\"  # Default self.folder path
        self.processed_image = None
        self.num_frames = 1
        self.num_copies_comp = ImageCountNumberComponent()

        self.setFixedSize(600, 600)

        # Create the main layout for the DropArea
        main_layout = QVBoxLayout(self)

        # 1st Layout: JPEG and GIF buttons
        button_layout = QHBoxLayout()
        self.jpg_button = QPushButton("JPEG", self)
        self.jpg_button.setMinimumWidth(200)
        self.gif_button = QPushButton("GIF", self)
        self.gif_button.setMinimumWidth(200)

        # Create a button group to manage the selection
        self.button_group = QButtonGroup(self)  # Create a button group
        self.button_group.addButton(self.jpg_button)  # Add JPEG button to the group
        self.button_group.addButton(self.gif_button)  # Add GIF button to the group

        # Connect button clicked signals to update styles
        self.jpg_button.clicked.connect(lambda: self.update_button_styles("JPEG"))
        self.gif_button.clicked.connect(lambda: self.update_button_styles("GIF"))

        button_layout.addStretch(1)
        button_layout.addWidget(self.jpg_button)
        button_layout.addWidget(self.gif_button)
        button_layout.addStretch(1)
        main_layout.addLayout(button_layout)  # Add the button layout to the main layout

        ### ImageCountNumberComponent

        # Add the additional button layout to the main layout

        main_layout.addStretch(1)
        # Add the additional button layout to the main layout
        main_layout.addWidget(self.num_copies_comp)

        # 3rd Layout: Drag and drop area
        self.label = QLabel(
            f"""
            Drag and drop 2-3 JPEGs to be processed here.<br><br>
            Processed Image will be saved in: <br><br>
            <a href="desktop_path">{self.folder}</a>
            """,
            self,
        )
        self.label.setStyleSheet(
            """
                QLabel {
                    font-family: 'Arial';
                    border: none;
                    font-size: 16px;
                }
            """
        )
        self.label.setContentsMargins(0, 0, 0, 0)

        self.label.setOpenExternalLinks(False)  # Prevent default link behavior
        self.label.setTextInteractionFlags(
            Qt.TextBrowserInteraction
        )  # Enable text interaction
        self.label.linkActivated.connect(self.handle_link_activated)

        self.label.setAlignment(Qt.AlignCenter)

        # Image selection list frame
        self.image_sel_frame = QLabel()
        self.image_sel_frame.setStyleSheet("border:none")
        self.image_sel_grid_layout = QGridLayout(self.image_sel_frame)

        # Process Now button
        self.process_now_btn = QPushButton("Process Now")
        self.clear_all_btn = QPushButton("Clear All")
        self.process_now_btn.setStyleSheet(
            """
            QPushButton {
                    background-color: #0372CD;  /* Selected color */
                    color: white;
                    border: none;
                    border-radius: 8px;
                }
            QPushButton:hover {
                background-color: #4A6FA3;
            }
            """
        )
        self.clear_all_btn.setStyleSheet(
            """
            QPushButton {
                    background-color: #595959;  /* Selected color */
                    color: white;
                    border: none;
                    border-radius: 8px;
                }
            QPushButton:hover {
                background-color: #898989;
            }
            """
        )
        self.process_now_btn.setFixedWidth(200)
        self.clear_all_btn.setFixedWidth(200)
        self.process_now_btn.clicked.connect(self.process_units)
        self.clear_all_btn.clicked.connect(self.clear_layout)

        self.label_frame = QLabel()
        self.label_frame.setMinimumSize(300, 400)
        label_vbox_layout = QVBoxLayout(self.label_frame)
        label_vbox_layout.addWidget(self.label)
        label_vbox_layout.addWidget(self.image_sel_frame)

        process_hbox_layout = QHBoxLayout()
        process_hbox_layout.addStretch(1)
        process_hbox_layout.addWidget(self.clear_all_btn)
        process_hbox_layout.addWidget(self.process_now_btn)
        process_hbox_layout.addStretch(1)
        process_hbox_layout.setSpacing(20)
        label_vbox_layout.addLayout(process_hbox_layout)

        label_vbox_layout.setAlignment(
            self.process_now_btn, Qt.AlignHCenter | Qt.AlignVCenter
        )
        self.label_frame.setStyleSheet(
            """
                QLabel {
                    background-color: rgba(0, 0, 0, 0);
                    border: 2px dashed white;
                    border-radius: 10px
                }
            """
        )

        main_layout.addStretch(1)
        main_layout.addWidget(self.label_frame)

        # Set the initial selection to JPEG
        # Update styles to reflect the initial selection
        self.update_button_styles("JPEG")
        self.process_now_btn.hide()
        self.clear_all_btn.hide()

        self.setLayout(main_layout)  # Set the main layout for the DropArea

        self.setAcceptDrops(True)

    def clear_layout(self):
        layout = self.image_sel_grid_layout
        while layout.count() > 0:
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def update_button_styles(self, selected_button):
        self.setDisableProcessNow(False)
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
        self.process_now_btn.hide()
        self.clear_all_btn.hide()
        self.clear_layout()
        if self.is_jpg:
            self.image_sel_frame.hide()
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
            self.image_sel_frame.hide()
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
        # if link == "process_image":
        #     dialog = NumberOfCopiesDialog(self)
        #     if dialog.exec_() == QDialog.Accepted:
        #         self.num_copies_comp.num_copies = dialog.get_number_of_copies()
        #         if self.num_copies_comp.num_copies is not None:
        #             print(
        #                 f"Number of copies to save: {self.num_copies_comp.num_copies}"
        #             )
        #         else:
        #             self.num_copies_comp.num_copies = 1
        #             print("Invalid number of copies")
        if link == "desktop_path":
            self.folder = QFileDialog.getExistingDirectory(
                self, "Select Directory", self.folder
            )
            if self.folder:
                print(f"Selected directory: {self.folder}")
            else:
                self.folder = "D:\\"

        copy_text = "copy" if self.num_copies_comp.num_copies == 1 else "copies"
        self.label.setText(
            f"""
            Drag and drop GIF image to be processed here.<br><br>
            Processed Image will be saved in:<br><br>
            <a href="desktop_path">{self.folder}</a>
            """
        )

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            url = event.mimeData().urls()[0]
            url = url.toLocalFile().lower()
            if (url.endswith(".gif") and not self.is_jpg) or (
                imghdr.what(url) is not None
                and not url.endswith(".gif")
                and self.is_jpg
            ):
                event.acceptProposedAction()
                self.label_frame.setStyleSheet(
                    f"background-color: white; border: 2px dashed white; border-radius: 10px; font-family: 'Arial'; font-size: 20px;"
                )
                self.label.hide()
                if not url.endswith(".gif"):
                    self.image_sel_frame.show()
                    self.process_now_btn.show()
                    self.clear_all_btn.show()
                return

        event.ignore()

    def dragLeaveEvent(self, event):
        self.label_frame.setStyleSheet(
            f"background-color: rgba(0, 0, 58, 0); border: 2px dashed white; border-radius: 10px; font-family: 'Arial'; font-size: 20px;"
        )
        self.label.show()

    def updateMovie_v1(self, thread_obj, gif_path):
        self.gif_movie = QMovie(gif_path)
        self.gif_movie.setScaledSize(self.label_frame.size())
        self.label.setMovie(self.gif_movie)
        self.gif_movie.start()

    def updateMovie(self, thread_obj, gif_path):
        # Load the GIF using Pillow to get original dimensions
        with Image.open(gif_path) as img:
            original_size = img.size  # (width, height)

        print(original_size)

        # Calculate scaled size while maintaining aspect ratio
        scaled_size = self.calculate_fit_size(original_size, self.label_frame.size())

        # Create a QMovie and set its scaled size
        self.gif_movie = QMovie(gif_path)
        self.gif_movie.setScaledSize(scaled_size)  # Set the scaled size for the movie
        self.label.setMovie(self.gif_movie)
        self.gif_movie.start()

    def calculate_fit_size(self, original_size, target_size):
        """Calculate a new size to fit within target size while maintaining aspect ratio."""
        original_width, original_height = original_size

        if original_width == 0 or original_height == 0:
            return QSize(0, 0)  # Handle invalid size

        # Calculate scaling factors
        width_ratio = target_size.width() / original_width
        height_ratio = target_size.height() / original_height

        # Use the smaller ratio to ensure it fits within the target size
        scale_ratio = min(width_ratio, height_ratio)

        # Calculate new dimensions
        new_width = int(original_width * scale_ratio)
        new_height = int(original_height * scale_ratio)

        return QSize(new_width, new_height)

    def display_static_image(self, image_path):
        """Display a static image."""
        pixmap = QPixmap(image_path)
        self.label.setPixmap(
            pixmap.scaled(
                self.label.size(),
                aspectRatioMode=Qt.KeepAspectRatio,
                transformMode=Qt.SmoothTransformation,
            )
        )

    def setDisableProcessNow(self, flag: bool):
        self.process_now_btn.setDisabled(flag)
        if flag:
            self.process_now_btn.setStyleSheet(
                """
                QPushButton {
                        background-color: #898989;  /* Selected color */
                        color: white;
                        border: none;
                        border-radius: 8px;
                    }
                """
            )
        else:
            self.process_now_btn.setStyleSheet(
                """
                QPushButton {
                        background-color: #0372CD;  /* Selected color */
                        color: white;
                        border: none;
                        border-radius: 8px;
                    }
                QPushButton:hover {
                    background-color: #4A6FA3;
                }
                """
            )

    def process_units(self):
        print("processing units...")

        self.setDisableProcessNow(True)

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

        if self.is_jpg:
            self.file_paths = []
            for i in range(self.image_sel_grid_layout.count()):
                item = self.image_sel_grid_layout.itemAt(i)
                if item.widget() and isinstance(item.widget(), ImagePanel):
                    self.file_paths.append(item.widget().file_path)

        # Start processing in a new thread
        self.processing_thread = GifProcessingThread(
            self.label,
            self.file_paths,
            self.num_copies_comp.num_copies,
            self.folder,
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
        self.processing_thread.update_image.connect(self.display_static_image)
        self.processing_thread.start()

        self.setDisableProcessNow(False)

    def dropEvent(self, event: QDropEvent):
        self.label_frame.setStyleSheet(
            f"background-color: rgba(0, 0, 58, 0); border: 2px dashed white; border-radius: 10px; font-family: 'Arial'; font-size: 20px;"
        )
        self.label.show()

        self.file_paths = [url.toLocalFile() for url in event.mimeData().urls()]
        # self.processGif(files[0])
        # gif_path = self.file_paths[0]
        # self.updateMovie(gif_path)

        if not self.is_jpg:
            self.process_units()
        else:
            for url in self.file_paths:
                self.addImagePanel(url)

    def addImagePanel(self, file_path):

        # Check for duplicates
        for i in range(self.image_sel_grid_layout.count()):
            item = self.image_sel_grid_layout.itemAt(i)
            if item.widget() and isinstance(item.widget(), ImagePanel):
                if item.widget().file_path == file_path:
                    return

        # If no duplicates, proceed to add the new panel
        panel = ImagePanel(file_path)
        current_count = self.image_sel_grid_layout.count()

        # Define maximum rows and columns
        max_rows = 2
        max_columns = 4

        if current_count < max_rows * max_columns:
            row = current_count // max_columns
            column = current_count % max_columns
            self.image_sel_grid_layout.addWidget(panel, row, column)

    def reset(self):
        # Stop any GIF animation
        if hasattr(self, "gif_movie") and self.gif_movie:
            self.gif_movie.stop()
            self.gif_movie = None
            delattr(self, "gif_movie")

        self.setAcceptDrops(True)
        self.label_frame.setStyleSheet(
            f"background-color: rgba(0, 0, 58, 0); border: 2px dashed white; border-radius: 10px; font-family: 'Arial'; font-size: 20px;"
        )
        # self.setFixedSize(460, 460)

        # Reset the label to its original state
        # self.label.clear()
        copy_text = "copy" if self.num_copies_comp.num_copies == 1 else "copies"
        self.label.setText(
            f"""
            Drag and drop GIF image to be processed here.<br><br>
            Processed Image will be saved in:<br><br>
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
                    f"Processed Image saved successfully (x{self.num_copies_comp.num_copies}). Time taken: {processing_time:.2f} seconds.",
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
                label="Visit Holograil", launch="https://www.thegrail.app"
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
        self.setWindowIcon(QIcon("C:\\ProgramData\\app_icon.ico"))

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
        pixmap = QPixmap("C:\\ProgramData\\logo.png")
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
        left_pixmap = QPixmap("C:\\ProgramData\\left.png")
        scaled_left = left_pixmap.scaled(
            230, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation
        )
        left_label.setPixmap(scaled_left)

        # Right image
        right_label = QLabel()
        right_pixmap = QPixmap("C:\\ProgramData\\right.png")
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

    def show_error_message(self, error_message):
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Critical)
        msg_box.setWindowTitle("Error")
        msg_box.setText("An error occurred:")
        msg_box.setInformativeText(error_message)
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec_()

    def compare_license(self, input):
        try:
            mac_address = get_mac_address()
            url = "http://ec2-52-90-200-142.compute-1.amazonaws.com:8088/subscriptions/validate-license"
            params = {
                "license_key": input,
                "device_address": mac_address,
            }
            response = requests.post(url, params=params, timeout=3)
            response.raise_for_status()
            # return response.status_code == 200
            return True
        except Exception as e:
            self.show_error_message(str(e.args[0]))
        return False
        # return True

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
    update_image = pyqtSignal(object, str)

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
        self.logger = logging.getLogger(__name__)
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
        self.current_image_index = 0
        self.image_display_timer = None

    def setup_timer(self):
        self.logger.info("Setting up timer!")
        self.image_display_timer = QTimer()
        self.image_display_timer.timeout.connect(self.show_next_image)
        self.image_display_timer.start(300)

    def stop_timer(self):
        if self.image_display_timer:
            self.image_display_timer.stop()
            self.logger.info("Timer stopped.")

    def show_next_image(self):
        self.logger.info(f"Current file paths: {self.file_paths}")
        self.logger.info(f"Current image index: {self.current_image_index}")

        if self.current_image_index < len(self.file_paths):
            self.update_image.emit(self, self.file_paths[self.current_image_index])
            self.current_image_index += 1
        else:
            self.stop_timer()

    def run(self):
        try:
            start_time = time.time()
            self.setup_timer()

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
                self.current_image_index = 0
                self.image_display_timer.start(300)
                self.logger.info("Timer started.")

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
            print(e.args[0])
            self.show_error_message(str(e.args[0]))

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
    shutil.copyfile("./resources/left.png", "C:\\ProgramData\\left.png")
    shutil.copyfile("./resources/logo.png", "C:\\ProgramData\\logo.png")
    shutil.copyfile("./resources/right.png", "C:\\ProgramData\\right.png")
    main()
