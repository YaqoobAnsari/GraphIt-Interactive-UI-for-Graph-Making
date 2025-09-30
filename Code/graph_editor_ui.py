from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QFileDialog, QToolBar, QLabel, QCheckBox,
                             QSpinBox, QMessageBox, QSlider, QGroupBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction
from canvas import GraphCanvas
from graph_manager import GraphManager
import os

class GraphEditorUI(QMainWindow):
    """Main window for the Graph Editor application."""
    
    def __init__(self):
        super().__init__()
        self.graph_manager = GraphManager()
        self.current_json_path = None
        self.current_image_path = None
        
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("Graph Editor - Network Overlay Tool")
        self.setGeometry(100, 100, 1600, 900)
        
        # Create central widget with main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        
        # Left panel for controls
        left_panel = self.create_left_panel()
        main_layout.addWidget(left_panel)
        
        # Canvas in the center
        canvas_layout = QVBoxLayout()
        self.create_toolbar()
        self.canvas = GraphCanvas(self.graph_manager)
        canvas_layout.addWidget(self.canvas)
        self.create_control_panel(canvas_layout)
        
        main_layout.addLayout(canvas_layout, stretch=1)
        
        # Status bar
        self.statusBar().showMessage("Ready - Load a JSON and Image to begin")
        
    def create_left_panel(self):
        """Create left control panel with sliders."""
        panel = QWidget()
        panel.setMaximumWidth(250)
        panel.setMinimumWidth(250)
        layout = QVBoxLayout(panel)
        
        # Node Type Selection for Adding
        type_group = QGroupBox("Node Type (for adding)")
        type_layout = QVBoxLayout()
        
        self.radio_room = QPushButton("Room")
        self.radio_room.setCheckable(True)
        self.radio_room.setChecked(True)
        self.radio_room.clicked.connect(lambda: self.set_add_node_type('room'))
        
        self.radio_door = QPushButton("Door")
        self.radio_door.setCheckable(True)
        self.radio_door.clicked.connect(lambda: self.set_add_node_type('door'))
        
        self.radio_corridor = QPushButton("Corridor")
        self.radio_corridor.setCheckable(True)
        self.radio_corridor.clicked.connect(lambda: self.set_add_node_type('corridor'))
        
        self.radio_outside = QPushButton("Outside")
        self.radio_outside.setCheckable(True)
        self.radio_outside.clicked.connect(lambda: self.set_add_node_type('outside'))
        
        self.radio_transition = QPushButton("Transition")
        self.radio_transition.setCheckable(True)
        self.radio_transition.clicked.connect(lambda: self.set_add_node_type('transition'))
        
        # Style for node type buttons
        button_style = """
            QPushButton {
                padding: 5px;
                text-align: left;
            }
            QPushButton:checked {
                background-color: #2196F3;
                color: white;
                font-weight: bold;
            }
        """
        self.radio_room.setStyleSheet(button_style)
        self.radio_door.setStyleSheet(button_style)
        self.radio_corridor.setStyleSheet(button_style)
        self.radio_outside.setStyleSheet(button_style)
        self.radio_transition.setStyleSheet(button_style)
        
        type_layout.addWidget(self.radio_room)
        type_layout.addWidget(self.radio_door)
        type_layout.addWidget(self.radio_corridor)
        type_layout.addWidget(self.radio_outside)
        type_layout.addWidget(self.radio_transition)
        
        type_group.setLayout(type_layout)
        layout.addWidget(type_group)
        
        # Node Size Controls
        size_group = QGroupBox("Node Size Controls")
        size_layout = QVBoxLayout()
        
        # Room nodes
        size_layout.addWidget(QLabel("Room/Door/Outside:"))
        self.slider_room = QSlider(Qt.Orientation.Horizontal)
        self.slider_room.setRange(4, 20)
        self.slider_room.setValue(8)
        self.slider_room.valueChanged.connect(lambda v: self.update_node_size('room', v))
        self.label_room = QLabel("8 px")
        size_layout.addWidget(self.slider_room)
        size_layout.addWidget(self.label_room)
        
        size_layout.addSpacing(10)
        
        # Corridor nodes
        size_layout.addWidget(QLabel("Corridor:"))
        self.slider_corridor = QSlider(Qt.Orientation.Horizontal)
        self.slider_corridor.setRange(2, 15)
        self.slider_corridor.setValue(4)
        self.slider_corridor.valueChanged.connect(lambda v: self.update_node_size('corridor', v))
        self.label_corridor = QLabel("4 px")
        size_layout.addWidget(self.slider_corridor)
        size_layout.addWidget(self.label_corridor)
        
        size_layout.addSpacing(10)
        
        # Transition nodes
        size_layout.addWidget(QLabel("Transition:"))
        self.slider_transition = QSlider(Qt.Orientation.Horizontal)
        self.slider_transition.setRange(4, 20)
        self.slider_transition.setValue(9)
        self.slider_transition.valueChanged.connect(lambda v: self.update_node_size('transition', v))
        self.label_transition = QLabel("9 px")
        size_layout.addWidget(self.slider_transition)
        size_layout.addWidget(self.label_transition)
        
        size_group.setLayout(size_layout)
        layout.addWidget(size_group)
        
        # Edge Width Control
        edge_group = QGroupBox("Edge Width")
        edge_layout = QVBoxLayout()
        
        self.slider_edge = QSlider(Qt.Orientation.Horizontal)
        self.slider_edge.setRange(1, 10)
        self.slider_edge.setValue(2)
        self.slider_edge.valueChanged.connect(lambda v: self.update_edge_width(v))
        self.label_edge = QLabel("2 px")
        edge_layout.addWidget(self.slider_edge)
        edge_layout.addWidget(self.label_edge)
        
        edge_group.setLayout(edge_layout)
        layout.addWidget(edge_group)
        
        layout.addStretch()
        
        return panel
    
    def set_add_node_type(self, node_type):
        """Set the node type for adding new nodes."""
        # Uncheck all buttons
        self.radio_room.setChecked(False)
        self.radio_door.setChecked(False)
        self.radio_corridor.setChecked(False)
        self.radio_outside.setChecked(False)
        self.radio_transition.setChecked(False)
        
        # Check the selected one
        if node_type == 'room':
            self.radio_room.setChecked(True)
        elif node_type == 'door':
            self.radio_door.setChecked(True)
        elif node_type == 'corridor':
            self.radio_corridor.setChecked(True)
        elif node_type == 'outside':
            self.radio_outside.setChecked(True)
        elif node_type == 'transition':
            self.radio_transition.setChecked(True)
            
        self.canvas.add_node_type = node_type
        
    def update_node_size(self, node_type, value):
        """Update node size for a specific type."""
        if node_type == 'room':
            self.canvas.node_size_room = value
            self.label_room.setText(f"{value} px")
        elif node_type == 'corridor':
            self.canvas.node_size_corridor = value
            self.label_corridor.setText(f"{value} px")
        elif node_type == 'transition':
            self.canvas.node_size_transition = value
            self.label_transition.setText(f"{value} px")
        self.canvas.update()
        
    def update_edge_width(self, value):
        """Update edge width."""
        self.canvas.edge_width = value
        self.label_edge.setText(f"{value} px")
        self.canvas.update()
        
    def create_toolbar(self):
        """Create the main toolbar with file operations."""
        toolbar = QToolBar("Main Toolbar")
        toolbar.setMovable(False)
        self.addToolBar(toolbar)
        
        # Load JSON
        load_json_action = QAction("Load JSON", self)
        load_json_action.triggered.connect(self.load_json)
        toolbar.addAction(load_json_action)
        
        # Load Image
        load_image_action = QAction("Load Image", self)
        load_image_action.triggered.connect(self.load_image)
        toolbar.addAction(load_image_action)
        
        toolbar.addSeparator()
        
        # Export
        export_action = QAction("Export", self)
        export_action.triggered.connect(self.export_data)
        toolbar.addAction(export_action)
        
        toolbar.addSeparator()
        
        # Clear
        clear_action = QAction("Clear All", self)
        clear_action.triggered.connect(self.clear_all)
        toolbar.addAction(clear_action)
        
        toolbar.addSeparator()
        
        # Statistics
        stats_action = QAction("Stats", self)
        stats_action.triggered.connect(self.show_stats)
        toolbar.addAction(stats_action)
        
    def create_control_panel(self, parent_layout):
        """Create the control panel with editing tools."""
        control_panel = QWidget()
        control_layout = QHBoxLayout(control_panel)
        
        # Mode buttons
        self.btn_pan = QPushButton("Pan")
        self.btn_pan.setCheckable(True)
        self.btn_pan.clicked.connect(lambda: self.set_mode('pan'))
        self.btn_pan.setStyleSheet("""
            QPushButton:checked {
                background-color: #9C27B0;
                color: white;
                font-weight: bold;
            }
        """)
        
        self.btn_select = QPushButton("Select Mode")
        self.btn_select.setCheckable(True)
        self.btn_select.setChecked(True)
        self.btn_select.clicked.connect(lambda: self.set_mode('select'))
        self.btn_select.setStyleSheet("""
            QPushButton:checked {
                background-color: #4CAF50;
                color: white;
                font-weight: bold;
            }
        """)
        
        self.btn_add_node = QPushButton("Add Node")
        self.btn_add_node.setCheckable(True)
        self.btn_add_node.clicked.connect(lambda: self.set_mode('add_node'))
        self.btn_add_node.setStyleSheet("""
            QPushButton:checked {
                background-color: #2196F3;
                color: white;
                font-weight: bold;
            }
        """)
        
        self.btn_add_edge = QPushButton("Add Edge")
        self.btn_add_edge.setCheckable(True)
        self.btn_add_edge.clicked.connect(lambda: self.set_mode('add_edge'))
        self.btn_add_edge.setStyleSheet("""
            QPushButton:checked {
                background-color: #FF9800;
                color: white;
                font-weight: bold;
            }
        """)
        
        self.btn_delete_node = QPushButton("Delete Node")
        self.btn_delete_node.setCheckable(True)
        self.btn_delete_node.clicked.connect(lambda: self.set_mode('delete_node'))
        self.btn_delete_node.setStyleSheet("""
            QPushButton:checked {
                background-color: #F44336;
                color: white;
                font-weight: bold;
            }
        """)
        
        self.btn_delete_edge = QPushButton("Delete Edge")
        self.btn_delete_edge.setCheckable(True)
        self.btn_delete_edge.clicked.connect(lambda: self.set_mode('delete_edge'))
        self.btn_delete_edge.setStyleSheet("""
            QPushButton:checked {
                background-color: #E91E63;
                color: white;
                font-weight: bold;
            }
        """)
        
        control_layout.addWidget(self.btn_pan)
        control_layout.addWidget(self.btn_select)
        control_layout.addWidget(self.btn_add_node)
        control_layout.addWidget(self.btn_add_edge)
        control_layout.addWidget(self.btn_delete_node)
        control_layout.addWidget(self.btn_delete_edge)
        
        control_layout.addStretch()
        
        # Grid toggle
        self.chk_grid = QCheckBox("Show Grid")
        self.chk_grid.setChecked(True)
        self.chk_grid.stateChanged.connect(self.toggle_grid)
        control_layout.addWidget(self.chk_grid)
        
        # Grid size
        control_layout.addWidget(QLabel("Grid Size:"))
        self.spin_grid_size = QSpinBox()
        self.spin_grid_size.setRange(10, 100)
        self.spin_grid_size.setValue(20)
        self.spin_grid_size.valueChanged.connect(self.change_grid_size)
        control_layout.addWidget(self.spin_grid_size)
        
        parent_layout.addWidget(control_panel)
        
    def set_mode(self, mode):
        """Set the current editing mode."""
        # Uncheck all buttons
        self.btn_pan.setChecked(False)
        self.btn_select.setChecked(False)
        self.btn_add_node.setChecked(False)
        self.btn_add_edge.setChecked(False)
        self.btn_delete_node.setChecked(False)
        self.btn_delete_edge.setChecked(False)
        
        # Check the selected button
        if mode == 'pan':
            self.btn_pan.setChecked(True)
        elif mode == 'select':
            self.btn_select.setChecked(True)
        elif mode == 'add_node':
            self.btn_add_node.setChecked(True)
        elif mode == 'add_edge':
            self.btn_add_edge.setChecked(True)
        elif mode == 'delete_node':
            self.btn_delete_node.setChecked(True)
        elif mode == 'delete_edge':
            self.btn_delete_edge.setChecked(True)
            
        self.canvas.set_mode(mode)
        
        # Update status message
        if mode == 'add_edge':
            self.statusBar().showMessage("Add Edge Mode: Click first node to start")
        else:
            self.statusBar().showMessage(f"Mode: {mode.replace('_', ' ').title()}")
        
    def toggle_grid(self, state):
        """Toggle grid visibility."""
        self.canvas.show_grid = (state == Qt.CheckState.Checked.value)
        self.canvas.update()
        
    def change_grid_size(self, value):
        """Change grid size."""
        self.canvas.grid_size = value
        self.canvas.update()
        
    def load_json(self):
        """Load a JSON file containing graph data."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Load Graph JSON", "Inputs/Jsons", "JSON Files (*.json)"
        )
        
        if file_path:
            if self.graph_manager.load_from_json(file_path):
                self.current_json_path = file_path
                self.canvas.update()
                stats = self.graph_manager.get_graph_stats()
                self.statusBar().showMessage(
                    f"Loaded: {os.path.basename(file_path)} | "
                    f"Nodes: {stats['node_count']} | Edges: {stats['edge_count']}"
                )
            else:
                QMessageBox.warning(
                    self, "Error", 
                    "Failed to load JSON file. Check console for details."
                )
                
    def load_image(self):
        """Load a background image (floor plan)."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Load Floor Plan Image", "Inputs/Plans", 
            "Images (*.png *.jpg *.jpeg *.bmp)"
        )
        
        if file_path:
            if self.canvas.load_background_image(file_path):
                self.current_image_path = file_path
                self.statusBar().showMessage(f"Image loaded: {os.path.basename(file_path)}")
            else:
                QMessageBox.warning(self, "Error", "Failed to load image")
                
    def export_data(self):
        """Export the current graph and image."""
        if not self.graph_manager.nodes:
            QMessageBox.warning(self, "Warning", "No graph data to export")
            return
            
        # Create Results directories if they don't exist
        os.makedirs("Results/Jsons", exist_ok=True)
        os.makedirs("Results/Images", exist_ok=True)
        
        # Get base filename
        if self.current_json_path:
            base_name = os.path.splitext(os.path.basename(self.current_json_path))[0]
        else:
            base_name = "graph_export"
            
        # Export JSON
        json_path = f"Results/Jsons/{base_name}_edited.json"
        if self.graph_manager.save_to_json(json_path):
            # Export image with overlay
            image_path = f"Results/Images/{base_name}_overlay.png"
            if self.canvas.export_image(image_path):
                QMessageBox.information(
                    self, "Success", 
                    f"Exported successfully!\n\nJSON: {json_path}\nImage: {image_path}"
                )
                self.statusBar().showMessage(f"Exported to: {json_path}")
            else:
                QMessageBox.warning(self, "Warning", "JSON exported but image export failed")
        else:
            QMessageBox.warning(self, "Error", "Failed to export data")
            
    def clear_all(self):
        """Clear all graph data."""
        reply = QMessageBox.question(
            self, "Confirm Clear", 
            "Are you sure you want to clear all nodes and edges?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.graph_manager.clear()
            self.canvas.update()
            self.statusBar().showMessage("Graph cleared")
            
    def show_stats(self):
        """Show graph statistics."""
        stats = self.graph_manager.get_graph_stats()
        msg = (
            f"Graph Statistics\n\n"
            f"Nodes: {stats['node_count']}\n"
            f"Edges: {stats['edge_count']}\n"
            f"Next Node ID: {stats['next_node_id']}\n\n"
        )
        
        if self.current_json_path:
            msg += f"JSON: {os.path.basename(self.current_json_path)}\n"
        if self.current_image_path:
            msg += f"Image: {os.path.basename(self.current_image_path)}"
            
        QMessageBox.information(self, "Statistics", msg)