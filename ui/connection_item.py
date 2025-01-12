from PySide6.QtWidgets import QGraphicsPathItem, QMenu
from PySide6.QtGui import QPainterPath, QPen, QColor
from PySide6.QtCore import Qt, QPointF
import math

class ConnectionItem(QGraphicsPathItem):
    def __init__(self, start_node, end_node, canvas):
        super().__init__()
        
        self.start_node = start_node
        self.end_node = end_node
        self.canvas = canvas
        self.temp_end = None
        
        # Set visual properties
        self.setZValue(-1)  # Draw under nodes
        self.setFlags(QGraphicsPathItem.ItemIsSelectable)
        self.setAcceptHoverEvents(True)
        
        self.update_style()
        self.update_position()

    def update_style(self):
        """Update the connection's visual style."""
        if self.start_node:
            # Use start node's color unless it's too light
            color = QColor(self.start_node.color)
            if color.lightness() > 240:
                color = QColor(Qt.black)
        else:
            color = QColor(Qt.black)
        
        # Create pen with rounded caps and joins
        pen = QPen(color, 2, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
        
        if self.isSelected():
            pen.setColor(QColor("#2196F3"))
            pen.setWidth(3)
        elif self.isUnderMouse():
            pen.setColor(QColor("#4CAF50"))
            pen.setWidth(2.5)
            
        self.setPen(pen)

    def update_position(self):
        """Update the connection path."""
        if not self.start_node:
            return
            
        path = QPainterPath()
        
        # Get center points of nodes
        start_pos = self.start_node.scenePos()
        start_pos = QPointF(
            start_pos.x() + self.start_node.boundingRect().width() / 2,
            start_pos.y() + self.start_node.boundingRect().height() / 2
        )
        
        if self.end_node:
            end_pos = self.end_node.scenePos()
            end_pos = QPointF(
                end_pos.x() + self.end_node.boundingRect().width() / 2,
                end_pos.y() + self.end_node.boundingRect().height() / 2
            )
        elif self.temp_end:
            end_pos = self.temp_end
        else:
            end_pos = start_pos

        # Calculate distance-based control points
        dx = end_pos.x() - start_pos.x()
        dy = end_pos.y() - start_pos.y()
        distance = math.sqrt(dx * dx + dy * dy)
        
        # Control point distance is proportional to total distance
        ctrl_dist = min(distance * 0.5, 200)
        
        # Calculate control points with better curve handling
        angle = math.atan2(dy, dx)
        
        # First control point
        ctrl1 = QPointF(
            start_pos.x() + ctrl_dist * math.cos(angle),
            start_pos.y() + ctrl_dist * math.sin(angle)
        )
        
        # Second control point
        ctrl2 = QPointF(
            end_pos.x() - ctrl_dist * math.cos(angle),
            end_pos.y() - ctrl_dist * math.sin(angle)
        )

        # Create curved path
        path.moveTo(start_pos)
        path.cubicTo(ctrl1, ctrl2, end_pos)
        
        self.setPath(path)

    def update_temp_end(self, pos):
        """Update temporary end point during connection creation."""
        self.temp_end = pos
        self.update_position()

    def set_end_node(self, node):
        """Set the end node and finalize the connection."""
        self.end_node = node
        self.temp_end = None
        self.update_position()

    def contextMenuEvent(self, event):
        """Show context menu for connection."""
        menu = QMenu()
        delete_action = menu.addAction("Delete Connection")
        
        action = menu.exec_(event.screenPos())
        if action == delete_action:
            self.scene().removeItem(self)

    def hoverEnterEvent(self, event):
        """Handle hover enter event."""
        self.update_style()
        super().hoverEnterEvent(event)

    def hoverLeaveEvent(self, event):
        """Handle hover leave event."""
        self.update_style()
        super().hoverLeaveEvent(event)

    def mousePressEvent(self, event):
        """Handle mouse press for connection interaction."""
        if event.button() == Qt.LeftButton:
            event.accept()
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        """Handle mouse release for connection interaction."""
        if event.button() == Qt.LeftButton:
            event.accept()
        super().mouseReleaseEvent(event)