from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QColorDialog,
    QComboBox, QFileDialog, QTextEdit
)
from PySide6.QtGui import QColor
from PySide6.QtCore import Qt
import time

class AddIdeaDialog(QDialog):
    def __init__(self, parent=None, node_data=None):
        super().__init__(parent)
        self.setWindowTitle("Add/Edit Idea")
        self.setModal(True)
        
        # Initialize values
        self.node_data = node_data or {}
        self.selected_color = self.node_data.get('color', '#FFFFFF')
        self.selected_shape = self.node_data.get('shape', 'oval')
        self.selected_image = self.node_data.get('image')

        self._create_ui()
        self._populate_fields()

    def _create_ui(self):
        layout = QVBoxLayout(self)

        # Title
        layout.addWidget(QLabel("Title:"))
        self.title_edit = QLineEdit()
        layout.addWidget(self.title_edit)

        # Description
        layout.addWidget(QLabel("Description:"))
        self.description_edit = QTextEdit()
        self.description_edit.setMinimumHeight(60)
        layout.addWidget(self.description_edit)

        # Keywords
        layout.addWidget(QLabel("Keywords (comma separated):"))
        self.keywords_edit = QLineEdit()
        layout.addWidget(self.keywords_edit)

        # Color
        color_layout = QHBoxLayout()
        color_layout.addWidget(QLabel("Color:"))
        self.color_button = QPushButton()
        self.color_button.clicked.connect(self._pick_color)
        self._update_color_button()
        color_layout.addWidget(self.color_button)
        layout.addLayout(color_layout)

        # Shape
        shape_layout = QHBoxLayout()
        shape_layout.addWidget(QLabel("Shape:"))
        self.shape_combo = QComboBox()
        self.shape_combo.addItems(['oval', 'rectangle', 'triangle'])
        self.shape_combo.setCurrentText(self.selected_shape)
        shape_layout.addWidget(self.shape_combo)
        layout.addLayout(shape_layout)

        # Image
        image_layout = QHBoxLayout()
        image_layout.addWidget(QLabel("Image:"))
        self.image_button = QPushButton("Choose Image")
        self.image_button.clicked.connect(self._pick_image)
        image_layout.addWidget(self.image_button)
        
        self.clear_image_button = QPushButton("Clear")
        self.clear_image_button.clicked.connect(self._clear_image)
        self.clear_image_button.setVisible(bool(self.selected_image))
        image_layout.addWidget(self.clear_image_button)
        
        layout.addLayout(image_layout)

        # Buttons
        button_layout = QHBoxLayout()
        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self.accept)
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)
        layout.addLayout(button_layout)

    def _populate_fields(self):
        if self.node_data:
            self.title_edit.setText(self.node_data.get('title', ''))
            self.description_edit.setText(self.node_data.get('description', ''))
            self.keywords_edit.setText(', '.join(self.node_data.get('keywords', [])))
            if self.node_data.get('image'):
                self.image_button.setText(self.node_data['image'].split('/')[-1])

    def _pick_color(self):
        color = QColorDialog.getColor(QColor(self.selected_color))
        if color.isValid():
            self.selected_color = color.name()
            self._update_color_button()

    def _update_color_button(self):
        self.color_button.setStyleSheet(
            f"background-color: {self.selected_color}; "
            f"color: {'black' if QColor(self.selected_color).lightness() > 128 else 'white'};"
        )
        self.color_button.setText(self.selected_color)

    def _pick_image(self):
        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "Choose Image",
            "",
            "Images (*.png *.jpg *.jpeg *.bmp)"
        )
        if file_name:
            self.selected_image = file_name
            self.image_button.setText(file_name.split('/')[-1])
            self.clear_image_button.setVisible(True)

    def _clear_image(self):
        self.selected_image = None
        self.image_button.setText("Choose Image")
        self.clear_image_button.setVisible(False)

    def get_data(self):
        title = self.title_edit.text().strip()
        description = self.description_edit.toPlainText().strip()
        keywords = [k.strip() for k in self.keywords_edit.text().split(',') if k.strip()]
        
        return {
            'id': self.node_data.get('id', str(int(time.time() * 1000))),
            'title': title if title else "Untitled",
            'description': description,
            'keywords': keywords,
            'color': self.selected_color,
            'shape': self.shape_combo.currentText(),
            'image': self.selected_image,
            'position': self.node_data.get('position', {'x': 0, 'y': 0})
        }
