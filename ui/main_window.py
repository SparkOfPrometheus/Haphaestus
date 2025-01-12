from PySide6.QtWidgets import (
    QMainWindow, QMessageBox, QToolBar, QFileDialog
)
from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtCore import Qt, Slot
from ui.canvas import CanvasWidget
from ui.add_idea_dialog import AddIdeaDialog
from controllers.import_export import import_data, export_data

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Hephaestus Mind Mapping")
        self.setGeometry(100, 100, 1024, 768)

        # Set up canvas
        self.canvas = CanvasWidget()
        self.setCentralWidget(self.canvas)

        self._create_actions()
        self._create_menus()
        self._create_toolbar()
        self.statusBar().showMessage("Ready")

    def _create_actions(self):
        # File actions
        self.new_map_action = QAction("&New", self)
        self.new_map_action.setShortcut(QKeySequence.New)
        self.new_map_action.triggered.connect(self.on_new_map)

        self.open_action = QAction("&Open...", self)
        self.open_action.setShortcut(QKeySequence.Open)
        self.open_action.triggered.connect(self.on_open)

        self.save_action = QAction("&Save...", self)
        self.save_action.setShortcut(QKeySequence.Save)
        self.save_action.triggered.connect(self.on_save)

        # Node actions
        self.create_root_action = QAction("Create &Root Node", self)
        self.create_root_action.setShortcut("Ctrl+R")
        self.create_root_action.triggered.connect(self.on_create_root)

        self.add_child_action = QAction("Add &Child Node", self)
        self.add_child_action.setShortcut("Ctrl+N")
        self.add_child_action.triggered.connect(self.on_add_child)

        self.edit_node_action = QAction("&Edit Node", self)
        self.edit_node_action.setShortcut("Ctrl+E")
        self.edit_node_action.triggered.connect(self.on_edit_node)

        self.delete_node_action = QAction("&Delete Node", self)
        self.delete_node_action.setShortcut(QKeySequence.Delete)
        self.delete_node_action.triggered.connect(self.on_delete_node)

    def _create_menus(self):
        menu_bar = self.menuBar()

        # File menu
        file_menu = menu_bar.addMenu("&File")
        file_menu.addAction(self.new_map_action)
        file_menu.addAction(self.open_action)
        file_menu.addAction(self.save_action)
        file_menu.addSeparator()
        file_menu.addAction("E&xit", self.close, "Ctrl+Q")

        # Edit menu
        edit_menu = menu_bar.addMenu("&Edit")
        edit_menu.addAction(self.create_root_action)
        edit_menu.addAction(self.add_child_action)
        edit_menu.addSeparator()
        edit_menu.addAction(self.edit_node_action)
        edit_menu.addAction(self.delete_node_action)

    def _create_toolbar(self):
        toolbar = QToolBar()
        self.addToolBar(toolbar)
        toolbar.addAction(self.new_map_action)
        toolbar.addAction(self.open_action)
        toolbar.addAction(self.save_action)
        toolbar.addSeparator()
        toolbar.addAction(self.create_root_action)
        toolbar.addAction(self.add_child_action)
        toolbar.addAction(self.edit_node_action)
        toolbar.addAction(self.delete_node_action)

    @Slot()
    def on_new_map(self):
        if QMessageBox.question(self, "New Mind Map", 
                              "Clear the current mind map?",
                              QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
            self.canvas.clear_all()
            self.statusBar().showMessage("Created new mind map")

    @Slot()
    def on_open(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open Mind Map", "", "Mind Map Files (*.json);;All Files (*)"
        )
        if file_path:
            self.canvas.clear_all()
            import_data(file_path, self.canvas.add_node, self.canvas.add_connection)
            self.statusBar().showMessage(f"Opened: {file_path}")

    @Slot()
    def on_save(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Mind Map", "", "Mind Map Files (*.json);;All Files (*)"
        )
        if file_path:
            export_data(
                self.canvas.get_all_nodes(),
                self.canvas.get_all_connections(),
                file_path
            )
            self.statusBar().showMessage(f"Saved to: {file_path}")

    @Slot()
    def on_create_root(self):
        dialog = AddIdeaDialog(self)
        if dialog.exec():
            self.canvas.add_node(dialog.get_data())
            self.statusBar().showMessage("Created root node")

    @Slot()
    def on_add_child(self):
        selected = self.canvas.get_selected_node()
        if not selected:
            QMessageBox.warning(self, "No Selection", 
                              "Please select a parent node first.")
            return

        dialog = AddIdeaDialog(self)
        if dialog.exec():
            self.canvas.add_node(dialog.get_data(), parent_id=selected.id)
            self.statusBar().showMessage("Added child node")

    @Slot()
    def on_edit_node(self):
        node = self.canvas.get_selected_node()
        if not node:
            QMessageBox.warning(self, "No Selection", 
                              "Please select a node to edit.")
            return

        dialog = AddIdeaDialog(self, {
            'id': node.id,
            'title': node.title,
            'description': node.description,
            'keywords': node.keywords,
            'color': node.color,
            'shape': node.shape_type,
            'image': node.image_path
        })
        
        if dialog.exec():
            data = dialog.get_data()
            node.update_from_data(data)
            self.canvas.scene.update()
            self.statusBar().showMessage("Updated node")

    @Slot()
    def on_delete_node(self):
        node = self.canvas.get_selected_node()
        if not node:
            QMessageBox.warning(self, "No Selection", 
                              "Please select a node to delete.")
            return

        if QMessageBox.question(self, "Delete Node", 
                              "Delete the selected node?",
                              QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
            self.canvas.delete_node(node.id)
            self.statusBar().showMessage("Deleted node")
