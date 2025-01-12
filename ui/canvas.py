from PySide6.QtWidgets import QGraphicsView, QGraphicsScene
from PySide6.QtGui import QPainter, QBrush, QColor
from PySide6.QtCore import Qt, QPointF
import math
from ui.idea_node import IdeaNode
from ui.connection_item import ConnectionItem

class CanvasWidget(QGraphicsView):
    def __init__(self):
        super().__init__()
        
        # Set up scene
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        self.setRenderHint(QPainter.Antialiasing)
        
        # Enable scrollbars and rubberband selection
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.setDragMode(QGraphicsView.RubberBandDrag)
        
        # Set view properties
        self.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)
        self.setRenderHint(QPainter.Antialiasing)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
        
        # Initialize variables
        self.creating_connection = None
        self.last_pos = QPointF(0, 0)
        self.zoom_factor = 1.15
        
        # Set scene size
        self.scene.setSceneRect(-2000, -2000, 4000, 4000)
        
        # Set background
        self.scene.setBackgroundBrush(QBrush(QColor("#f0f0f0")))

    def add_node(self, idea_data, parent_id=None):
        """Add a new node to the canvas."""
        node = IdeaNode(
            node_id=idea_data['id'],
            title=idea_data['title'],
            description=idea_data.get('description', ''),
            color=idea_data['color'],
            shape=idea_data['shape'],
            keywords=idea_data.get('keywords', []),
            image_path=idea_data.get('image')
        )
        
        self.scene.addItem(node)
        
        # Position the node
        if parent_id:
            parent = self.get_node_by_id(parent_id)
            if parent:
                # Position relative to parent
                pos = parent.pos()
                offset = 200  # Increased distance from parent
                angle = len(self.get_all_nodes()) * math.pi / 6
                x = pos.x() + offset * math.cos(angle)
                y = pos.y() + offset * math.sin(angle)
                
                # Adjust position based on node size
                x -= node.boundingRect().width() / 2
                y -= node.boundingRect().height() / 2
                
                node.setPos(x, y)
                
                # Create connection to parent
                self.add_connection(parent.id, node.id)
        else:
            # Position new root node using spiral layout
            count = len(self.get_all_nodes())
            angle = count * math.pi / 6
            radius = 150 + count * 30  # Increased spacing
            x = radius * math.cos(angle)
            y = radius * math.sin(angle)
            
            # Adjust position based on node size
            x -= node.boundingRect().width() / 2
            y -= node.boundingRect().height() / 2
            
            node.setPos(x, y)
        
        return node

    def add_connection(self, source_id, target_id):
        """Add a connection between two nodes."""
        source = self.get_node_by_id(source_id)
        target = self.get_node_by_id(target_id)
        if source and target:
            conn = ConnectionItem(source, target, self)
            self.scene.addItem(conn)
            return conn
        return None

    def delete_node(self, node_id):
        """Delete a node and its connections."""
        node = self.get_node_by_id(node_id)
        if node:
            # Remove connected edges first
            for item in self.scene.items():
                if isinstance(item, ConnectionItem):
                    if item.start_node == node or item.end_node == node:
                        self.scene.removeItem(item)
            # Remove the node
            self.scene.removeItem(node)

    def clear_all(self):
        """Clear all items from the scene."""
        self.scene.clear()
        self.creating_connection = None

    def get_node_by_id(self, node_id):
        """Get a node by its ID."""
        for item in self.scene.items():
            if isinstance(item, IdeaNode) and item.id == node_id:
                return item
        return None

    def get_selected_node(self):
        """Get the currently selected node."""
        for item in self.scene.selectedItems():
            if isinstance(item, IdeaNode):
                return item
        return None

    def get_all_nodes(self):
        """Get all nodes in the scene."""
        return [item for item in self.scene.items() if isinstance(item, IdeaNode)]

    def get_all_connections(self):
        """Get all connections in the scene."""
        return [(item.start_node.id, item.end_node.id) 
                for item in self.scene.items()
                if isinstance(item, ConnectionItem)]

    def wheelEvent(self, event):
        """Handle zoom with mouse wheel."""
        if event.modifiers() == Qt.ControlModifier:
            factor = self.zoom_factor if event.angleDelta().y() > 0 else 1 / self.zoom_factor
            self.scale(factor, factor)
        else:
            super().wheelEvent(event)

    def mousePressEvent(self, event):
        """Handle mouse press events."""
        if event.modifiers() == Qt.ShiftModifier:
            item = self.itemAt(event.pos())
            if isinstance(item, IdeaNode):
                # Start connection creation
                self.creating_connection = ConnectionItem(item, None, self)
                self.scene.addItem(self.creating_connection)
                event.accept()
                return
        elif event.button() == Qt.MiddleButton:
            # Enable panning
            self.setDragMode(QGraphicsView.ScrollHandDrag)
            event.accept()
            return
        
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        """Handle mouse move events."""
        if self.creating_connection:
            scene_pos = self.mapToScene(event.pos())
            self.creating_connection.update_temp_end(scene_pos)
            event.accept()
            return
            
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        """Handle mouse release events."""
        if self.creating_connection:
            end_item = self.itemAt(event.pos())
            if isinstance(end_item, IdeaNode) and end_item != self.creating_connection.start_node:
                # Complete connection
                self.creating_connection.set_end_node(end_item)
            else:
                # Remove incomplete connection
                self.scene.removeItem(self.creating_connection)
            
            self.creating_connection = None
            event.accept()
            return
        elif event.button() == Qt.MiddleButton:
            # Restore rubber band selection
            self.setDragMode(QGraphicsView.RubberBandDrag)
            
        super().mouseReleaseEvent(event)