from PySide6.QtWidgets import (
    QGraphicsItem, QGraphicsTextItem, QMenu,
    QDialog, QVBoxLayout, QTextBrowser, QPushButton,
    QStyleOptionGraphicsItem, QStyle
)
from PySide6.QtGui import QPainter, QPen, QColor, QBrush, QPainterPath, QTextOption
from PySide6.QtCore import Qt, QRectF

class DescriptionDialog(QDialog):
    """Dialog for displaying node descriptions."""
    def __init__(self, title, description, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        
        layout = QVBoxLayout(self)
        
        # Description viewer
        text_browser = QTextBrowser()
        text_browser.setText(description)
        layout.addWidget(text_browser)
        
        # Close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)
        
        self.resize(400, 300)

class IdeaNode(QGraphicsItem):
    def __init__(self, node_id, title, description, color, shape, keywords, image_path=None):
        super().__init__()
        
        # Node data
        self.id = node_id
        self.title = title
        self.description = description
        self.color = color
        self.shape_type = shape.lower()
        self.keywords = keywords
        self.image_path = image_path
        
        # Visual properties
        self.width = 120
        self.height = 60
        self.padding = 10
        
        # Set flags
        self.setFlags(
            QGraphicsItem.ItemIsMovable |
            QGraphicsItem.ItemIsSelectable |
            QGraphicsItem.ItemSendsGeometryChanges
        )
        self.setAcceptHoverEvents(True)
        
        # Create text item
        self.text_item = QGraphicsTextItem(self)
        self.text_item.setDefaultTextColor(Qt.black)
        
        # Set text alignment
        text_option = QTextOption()
        text_option.setAlignment(Qt.AlignCenter)
        self.text_item.document().setDefaultTextOption(text_option)
        
        self.update_text()

    def boundingRect(self):
        return QRectF(0, 0, self.width, self.height)

    def paint(self, painter, option, widget=None):
        # Set up painter
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Set pen based on state
        if self.isSelected():
            pen = QPen(QColor("#2196F3"), 2)
        elif option.state & QStyle.State_MouseOver:
            pen = QPen(QColor("#4CAF50"), 2)
        else:
            pen = QPen(Qt.black, 1.5)
        painter.setPen(pen)
        
        # Set brush
        painter.setBrush(QBrush(QColor(self.color)))
        
        # Draw shape
        rect = self.boundingRect()
        if self.shape_type == 'rectangle':
            painter.drawRect(rect)
        elif self.shape_type == 'triangle':
            path = QPainterPath()
            path.moveTo(rect.center().x(), rect.top())
            path.lineTo(rect.right(), rect.bottom())
            path.lineTo(rect.left(), rect.bottom())
            path.closeSubpath()
            painter.drawPath(path)
        else:  # oval
            painter.drawEllipse(rect)

    def update_text(self):
        """Update the displayed text and adjust node size."""
        # Prepare display text
        text = self.title
        if self.keywords:
            text += f"\n[{', '.join(self.keywords)}]"
        
        self.text_item.setPlainText(text)
        
        # Calculate required size based on text
        text_rect = self.text_item.boundingRect()
        self.width = max(120, text_rect.width() + 2 * self.padding)
        self.height = max(60, text_rect.height() + 2 * self.padding)
        
        # Center text within node
        text_x = (self.width - text_rect.width()) / 2
        text_y = (self.height - text_rect.height()) / 2
        self.text_item.setPos(text_x, text_y)
        
        self.update()

    def shape(self):
        """Define the clickable area of the node."""
        path = QPainterPath()
        if self.shape_type == 'rectangle':
            path.addRect(self.boundingRect())
        elif self.shape_type == 'triangle':
            rect = self.boundingRect()
            path.moveTo(rect.center().x(), rect.top())
            path.lineTo(rect.right(), rect.bottom())
            path.lineTo(rect.left(), rect.bottom())
            path.closeSubpath()
        else:  # oval
            path.addEllipse(self.boundingRect())
        return path

    def contextMenuEvent(self, event):
        """Handle right-click context menu."""
        menu = QMenu()
        
        # Add menu items
        view_desc_action = None
        if self.description:
            view_desc_action = menu.addAction("View Description")
        edit_action = menu.addAction("Edit")
        delete_action = menu.addAction("Delete")
        
        # Show menu and handle selection
        action = menu.exec_(event.screenPos())
        
        if action:
            if view_desc_action and action == view_desc_action:
                dialog = DescriptionDialog(self.title, self.description)
                dialog.exec_()
            elif action == edit_action:
                self.scene().views()[0].parent().on_edit_node()
            elif action == delete_action:
                self.scene().views()[0].parent().on_delete_node()

    def update_from_data(self, data):
        """Update node properties from data dictionary."""
        self.title = data['title']
        self.description = data.get('description', '')
        self.keywords = data.get('keywords', [])
        self.color = data['color']
        self.shape_type = data['shape']
        self.image_path = data.get('image')
        self.update_text()
        self.update()

    def itemChange(self, change, value):
        """Handle item changes."""
        if change == QGraphicsItem.ItemPositionChange and self.scene():
            # Update connected edges
            for item in self.scene().items():
                if hasattr(item, 'update_position'):
                    if hasattr(item, 'start_node') and item.start_node == self:
                        item.update_position()
                    elif hasattr(item, 'end_node') and item.end_node == self:
                        item.update_position()
        
        return super().itemChange(change, value)