from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt, QPointF, QRectF
from PyQt6.QtGui import QPainter, QPen, QBrush, QColor, QPixmap, QPainterPath, QRadialGradient, QFont
import math

class GraphCanvas(QWidget):
    """Canvas widget for displaying and editing the graph."""
    
    def __init__(self, graph_manager):
        super().__init__()
        self.graph_manager = graph_manager
        self.background_image = None
        self.mode = 'select'
        self.selected_node = None
        self.selected_edge = None
        self.edge_start_node = None
        self.show_grid = True
        self.grid_size = 20
        self.dragging_node = None
        self.drag_offset = QPointF(0, 0)
        
        # Callback for status updates
        self.status_callback = None
        
        # Pan and zoom
        self.panning = False
        self.pan_start = QPointF(0, 0)
        self.pan_offset = QPointF(0, 0)
        self.zoom_level = 1.0
        
        # Image transformation parameters
        self.image_offset_x = 0
        self.image_offset_y = 0
        self.image_scale = 1.0
        self.original_image_size = (0, 0)
        
        # Configurable sizes (controlled by sliders)
        self.node_size_room = 8
        self.node_size_corridor = 4
        self.node_size_transition = 9
        self.edge_width = 2
        
        # Node type for adding new nodes
        self.add_node_type = 'room'
        
        self.setMinimumSize(800, 600)
        self.setMouseTracking(True)
        
        # Color scheme
        self.node_colors = {
            'room': QColor(255, 128, 0),        # Bright Orange
            'door': QColor(0, 204, 102),        # Emerald Green
            'corridor': QColor(255, 102, 255),  # Magenta
            'outside': QColor(204, 51, 51),     # Crimson Red
            'transition': QColor(0, 0, 255),    # Red
            'unknown': QColor(128, 128, 128),   # Gray
        }
        
        # Glow colors for each node type
        self.glow_colors = {
            'room': QColor(255, 165, 0),        # Orange glow
            'door': QColor(0, 255, 127),        # Green glow
            'corridor': QColor(255, 20, 147),   # Pink glow
            'outside': QColor(255, 69, 0),      # Red-orange glow
            'transition': QColor(135, 206, 250), # Sky blue glow
            'unknown': QColor(169, 169, 169),   # Gray glow
        }
        
        self.edge_colors = {
            'room': QColor(255, 165, 0),
            'corridor': QColor(51, 153, 255),
            'outside': QColor(255, 0, 0),
            'transition': QColor(0, 0, 180),
        }
        
        self.edge_selected_color = QColor(255, 100, 100)
        self.grid_color = QColor(200, 200, 200, 100)
        
    def load_background_image(self, image_path):
        """Load a background image and calculate transformation."""
        self.background_image = QPixmap(image_path)
        if not self.background_image.isNull():
            self.original_image_size = (self.background_image.width(), self.background_image.height())
            self.calculate_image_transform()
            self.update()
            return True
        return False
        
    def calculate_image_transform(self):
        """Calculate scale and offset to fit image in canvas."""
        if not self.background_image or self.background_image.isNull():
            return
            
        img_w = self.background_image.width()
        img_h = self.background_image.height()
        canvas_w = self.width()
        canvas_h = self.height()
        
        # Calculate scale to fit while maintaining aspect ratio
        scale_w = canvas_w / img_w
        scale_h = canvas_h / img_h
        self.image_scale = min(scale_w, scale_h) * self.zoom_level
        
        # Calculate offset to center the image
        scaled_w = img_w * self.image_scale
        scaled_h = img_h * self.image_scale
        self.image_offset_x = (canvas_w - scaled_w) / 2 + self.pan_offset.x()
        self.image_offset_y = (canvas_h - scaled_h) / 2 + self.pan_offset.y()
        
    def image_to_canvas(self, x, y):
        """Transform coordinates from original image space to canvas space."""
        canvas_x = x * self.image_scale + self.image_offset_x
        canvas_y = y * self.image_scale + self.image_offset_y
        return QPointF(canvas_x, canvas_y)
        
    def canvas_to_image(self, canvas_x, canvas_y):
        """Transform coordinates from canvas space to original image space."""
        img_x = (canvas_x - self.image_offset_x) / self.image_scale
        img_y = (canvas_y - self.image_offset_y) / self.image_scale
        return (img_x, img_y)
        
    def resizeEvent(self, event):
        """Recalculate transformation on resize."""
        super().resizeEvent(event)
        self.calculate_image_transform()
        
    def wheelEvent(self, event):
        """Handle mouse wheel for zooming."""
        if event.angleDelta().y() > 0:
            self.zoom_level *= 1.1
        else:
            self.zoom_level *= 0.9
            
        self.zoom_level = max(0.1, min(5.0, self.zoom_level))
        self.calculate_image_transform()
        self.update()
        
    def set_mode(self, mode):
        """Set the current editing mode."""
        self.mode = mode
        
        # Reset edge start when changing modes
        if mode != 'add_edge':
            self.edge_start_node = None
            
        self.selected_node = None
        self.selected_edge = None
        
        # Update cursor based on mode
        if mode == 'pan':
            self.setCursor(Qt.CursorShape.OpenHandCursor)
        else:
            self.setCursor(Qt.CursorShape.ArrowCursor)
            
        self.update()
        
    def snap_to_grid(self, point):
        """Snap a point to the nearest grid intersection."""
        if self.show_grid:
            x = round(point.x() / self.grid_size) * self.grid_size
            y = round(point.y() / self.grid_size) * self.grid_size
            return QPointF(x, y)
        return point
        
    def get_node_color(self, node_id):
        """Get color for a node based on its type."""
        node_data = self.graph_manager.nodes.get(node_id, {})
        node_type = node_data.get('type', 'unknown').lower()
        return self.node_colors.get(node_type, self.node_colors['unknown'])
        
    def get_glow_color(self, node_id):
        """Get glow color for a node based on its type."""
        node_data = self.graph_manager.nodes.get(node_id, {})
        node_type = node_data.get('type', 'unknown').lower()
        return self.glow_colors.get(node_type, self.glow_colors['unknown'])
        
    def get_node_radius(self, node_id):
        """Get radius for a node based on its type."""
        node_data = self.graph_manager.nodes.get(node_id, {})
        node_type = node_data.get('type', 'unknown').lower()
        
        if node_type == 'corridor':
            return self.node_size_corridor
        elif node_type in ('transition', 'tranistion'):
            return self.node_size_transition
        else:
            return self.node_size_room
            
    def get_edge_color(self, node1_id, node2_id):
        """Get color for an edge based on connected node types."""
        type1 = self.graph_manager.nodes.get(node1_id, {}).get('type', 'unknown').lower()
        type2 = self.graph_manager.nodes.get(node2_id, {}).get('type', 'unknown').lower()
        
        if 'outside' in (type1, type2):
            return self.edge_colors['outside']
        if 'corridor' in (type1, type2):
            return self.edge_colors['corridor']
        if ('transition' in (type1, type2)) or ('tranistion' in (type1, type2)):
            return self.edge_colors['transition']
        return self.edge_colors['room']
        
    def paintEvent(self, event):
        """Paint the canvas."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Draw background
        painter.fillRect(self.rect(), QColor(245, 245, 245))
        
        # Draw background image
        if self.background_image and not self.background_image.isNull():
            scaled_pixmap = self.background_image.scaled(
                int(self.original_image_size[0] * self.image_scale),
                int(self.original_image_size[1] * self.image_scale),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            painter.drawPixmap(int(self.image_offset_x), int(self.image_offset_y), scaled_pixmap)
            
        # Draw grid
        if self.show_grid:
            self.draw_grid(painter)
            
        # Draw edges
        self.draw_edges(painter)
        
        # Draw nodes
        self.draw_nodes(painter)
        
        # Draw temporary edge when adding
        if self.mode == 'add_edge' and self.edge_start_node:
            self.draw_temp_edge(painter)
            
        # Draw legend
        self.draw_legend(painter)
        
        # Draw zoom info
        self.draw_zoom_info(painter)
            
    def draw_grid(self, painter):
        """Draw the grid."""
        painter.setPen(QPen(self.grid_color, 1))
        
        # Vertical lines
        for x in range(0, self.width(), self.grid_size):
            painter.drawLine(x, 0, x, self.height())
            
        # Horizontal lines
        for y in range(0, self.height(), self.grid_size):
            painter.drawLine(0, y, self.width(), y)
            
    def draw_legend(self, painter):
        """Draw color legend."""
        legend_x = 10
        legend_y = 10
        line_height = 25
        
        painter.setFont(QFont("Arial", 9))
        
        legend_items = [
            ("Room", self.node_colors['room']),
            ("Door", self.node_colors['door']),
            ("Corridor", self.node_colors['corridor']),
            ("Transition", self.node_colors['transition']),
            ("Outside", self.node_colors['outside']),
        ]
        
        # Draw legend background
        legend_width = 120
        legend_height = len(legend_items) * line_height + 10
        painter.fillRect(legend_x, legend_y, legend_width, legend_height, QColor(255, 255, 255, 200))
        painter.setPen(QPen(QColor(0, 0, 0), 1))
        painter.drawRect(legend_x, legend_y, legend_width, legend_height)
        
        # Draw legend items
        for i, (label, color) in enumerate(legend_items):
            y = legend_y + 10 + i * line_height
            painter.setBrush(QBrush(color))
            painter.drawEllipse(legend_x + 10, y, 12, 12)
            painter.setPen(QColor(0, 0, 0))
            painter.drawText(legend_x + 30, y + 10, label)
            
    def draw_zoom_info(self, painter):
        """Draw zoom level info."""
        zoom_text = f"Zoom: {self.zoom_level:.1f}x"
        painter.setFont(QFont("Arial", 9))
        painter.setPen(QColor(0, 0, 0))
        
        text_rect = QRectF(self.width() - 100, self.height() - 30, 90, 20)
        painter.fillRect(text_rect, QColor(255, 255, 255, 200))
        painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, zoom_text)
            
    def draw_nodes(self, painter):
        """Draw all nodes."""
        for node_id, node_data in self.graph_manager.nodes.items():
            # Transform coordinates from image space to canvas space
            canvas_pos = self.image_to_canvas(node_data['x'], node_data['y'])
            
            is_selected = (self.selected_node == node_id)
            is_edge_start = (self.edge_start_node == node_id and self.mode == 'add_edge')
            node_radius = self.get_node_radius(node_id)
            
            # Draw glow effect for selected node or edge start node
            if is_selected or is_edge_start:
                self.draw_node_glow(painter, canvas_pos, node_radius, node_id)
                
            # Draw node
            node_color = self.get_node_color(node_id)
            painter.setBrush(QBrush(node_color))
            
            if is_selected or is_edge_start:
                # Use different highlight for edge start node
                if is_edge_start and not is_selected:
                    painter.setPen(QPen(QColor(100, 100, 255), 3))  # Blue for edge start
                else:
                    painter.setPen(QPen(QColor(255, 200, 0), 3))  # Yellow for selected
            else:
                painter.setPen(QPen(QColor(0, 0, 0), 2))
                
            painter.drawEllipse(canvas_pos, node_radius, node_radius)
            
            # Draw node label (skip for corridor nodes unless selected or edge start)
            node_type = node_data.get('type', 'unknown').lower()
            if node_type != 'corridor' or is_selected or is_edge_start:
                painter.setPen(QPen(QColor(0, 0, 0)))
                painter.setFont(QFont("Arial", 8))
                painter.drawText(
                    QRectF(canvas_pos.x() - 50, canvas_pos.y() - 35, 100, 20),
                    Qt.AlignmentFlag.AlignCenter,
                    str(node_id)
                )
            
    def draw_node_glow(self, painter, pos, radius, node_id):
        """Draw a type-based glow effect around a node."""
        glow_color = self.get_glow_color(node_id)
        
        gradient = QRadialGradient(pos, radius * 3)
        gradient.setColorAt(0, QColor(glow_color.red(), glow_color.green(), glow_color.blue(), 120))
        gradient.setColorAt(0.5, QColor(glow_color.red(), glow_color.green(), glow_color.blue(), 60))
        gradient.setColorAt(1, QColor(glow_color.red(), glow_color.green(), glow_color.blue(), 0))
        
        painter.setBrush(QBrush(gradient))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(pos, radius * 3, radius * 3)
        
    def draw_edges(self, painter):
        """Draw all edges (without arrows)."""
        for edge in self.graph_manager.edges:
            node1_id, node2_id = edge
            
            if node1_id not in self.graph_manager.nodes or node2_id not in self.graph_manager.nodes:
                continue
                
            node1 = self.graph_manager.nodes[node1_id]
            node2 = self.graph_manager.nodes[node2_id]
            
            # Transform coordinates
            pos1 = self.image_to_canvas(node1['x'], node1['y'])
            pos2 = self.image_to_canvas(node2['x'], node2['y'])
            
            is_selected = (self.selected_edge == edge)
            
            # Draw edge highlight for selection
            if is_selected:
                painter.setPen(QPen(self.edge_selected_color, self.edge_width * 3, Qt.PenStyle.SolidLine))
                painter.drawLine(pos1, pos2)
                
            # Draw main edge
            if is_selected:
                painter.setPen(QPen(self.edge_selected_color, self.edge_width, Qt.PenStyle.SolidLine))
            else:
                edge_color = self.get_edge_color(node1_id, node2_id)
                painter.setPen(QPen(edge_color, self.edge_width, Qt.PenStyle.SolidLine))
                
            painter.drawLine(pos1, pos2)
        
    def draw_temp_edge(self, painter):
        """Draw a temporary edge while adding."""
        if self.edge_start_node in self.graph_manager.nodes:
            node = self.graph_manager.nodes[self.edge_start_node]
            start = self.image_to_canvas(node['x'], node['y'])
            
            # Get cursor position and convert to QPointF
            cursor_pos = self.mapFromGlobal(self.cursor().pos())
            end = QPointF(cursor_pos.x(), cursor_pos.y())
            
            painter.setPen(QPen(QColor(100, 100, 255, 150), self.edge_width, Qt.PenStyle.DashLine))
            painter.drawLine(start, end)
            
    def mousePressEvent(self, event):
        """Handle mouse press events."""
        pos = event.position()
        
        # Right-click in Add Edge mode - switch back to Select mode
        if self.mode == 'add_edge' and event.button() == Qt.MouseButton.RightButton:
            if self.status_callback:
                self.status_callback("Exiting Add Edge mode - switched to Select Mode")
            # Need to notify UI to change mode button states
            from PyQt6.QtWidgets import QApplication
            main_window = QApplication.instance().activeWindow()
            if main_window and hasattr(main_window, 'set_mode'):
                main_window.set_mode('select')
            self.update()
            return
        
        # Pan mode - left click and drag to pan
        if self.mode == 'pan':
            if event.button() == Qt.MouseButton.LeftButton:
                self.panning = True
                self.pan_start = pos
                self.setCursor(Qt.CursorShape.ClosedHandCursor)
            return
        
        # Middle mouse button for panning (works in all modes)
        if event.button() == Qt.MouseButton.MiddleButton:
            self.panning = True
            self.pan_start = pos
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
            return
        
        if self.mode == 'select':
            # Check if clicking on a node
            clicked_node = self.get_node_at_position(pos)
            if clicked_node:
                self.selected_node = clicked_node
                self.dragging_node = clicked_node
                node_data = self.graph_manager.nodes[clicked_node]
                canvas_pos = self.image_to_canvas(node_data['x'], node_data['y'])
                self.drag_offset = pos - canvas_pos
                self.selected_edge = None
            else:
                # Check if clicking on an edge
                clicked_edge = self.get_edge_at_position(pos)
                if clicked_edge:
                    self.selected_edge = clicked_edge
                    self.selected_node = None
                else:
                    self.selected_node = None
                    self.selected_edge = None
                    
        elif self.mode == 'add_node':
            # Convert canvas coordinates to image coordinates
            img_x, img_y = self.canvas_to_image(pos.x(), pos.y())
            node_id = self.graph_manager.add_node(img_x, img_y, type=self.add_node_type)
            self.selected_node = node_id
            print(f"Canvas: Created node with ID '{node_id}', type '{self.add_node_type}'")
            print(f"Canvas: Node exists in graph_manager.nodes: {node_id in self.graph_manager.nodes}")
            if self.status_callback:
                self.status_callback(f"Added node: {node_id} (type: {self.add_node_type})")
            
        elif self.mode == 'add_edge':
            # Only respond to left-click node selections
            if event.button() == Qt.MouseButton.LeftButton:
                clicked_node = self.get_node_at_position(pos)
                
                # Only respond to node clicks, ignore edge clicks
                if clicked_node:
                    print(f"Canvas: Clicked on node '{clicked_node}'")
                    print(f"Canvas: Node exists: {clicked_node in self.graph_manager.nodes}")
                    
                    if self.edge_start_node is None:
                        # First node selected - store it and wait for second
                        self.edge_start_node = clicked_node
                        self.selected_node = clicked_node  # Highlight the first node
                        print(f"Canvas: Set edge_start_node to '{clicked_node}'")
                        if self.status_callback:
                            self.status_callback(f"Edge start: {clicked_node}. Click second node (or right-click to exit)")
                    else:
                        # Second (or subsequent) node selected
                        print(f"Canvas: Attempting to add edge from '{self.edge_start_node}' to '{clicked_node}'")
                        if self.edge_start_node != clicked_node:
                            # Add edge from previous node to current node
                            success = self.graph_manager.add_edge(self.edge_start_node, clicked_node)
                            if success:
                                if self.status_callback:
                                    self.status_callback(f"Edge created: {self.edge_start_node} → {clicked_node}. Click next node or right-click to exit")
                            else:
                                if self.status_callback:
                                    self.status_callback(f"Could not create edge (check console for details)")
                        else:
                            print(f"Canvas: Same node clicked twice, just updating edge_start_node")
                            
                        # Set current node as the start for next edge (continuous mode)
                        self.edge_start_node = clicked_node
                        self.selected_node = clicked_node
                    
        elif self.mode == 'delete_node':
            clicked_node = self.get_node_at_position(pos)
            if clicked_node:
                self.graph_manager.remove_node(clicked_node)
                self.selected_node = None
                
        elif self.mode == 'delete_edge':
            clicked_edge = self.get_edge_at_position(pos)
            if clicked_edge:
                self.graph_manager.remove_edge(clicked_edge)
                self.selected_edge = None
                
        self.update()
        
    def mouseMoveEvent(self, event):
        """Handle mouse move events."""
        pos = event.position()
        
        if self.panning:
            delta = pos - self.pan_start
            self.pan_offset += delta
            self.pan_start = pos
            self.calculate_image_transform()
            self.update()
            return
            
        if self.mode == 'select' and self.dragging_node:
            canvas_pos = pos - self.drag_offset
            
            # Convert to image coordinates
            img_x, img_y = self.canvas_to_image(canvas_pos.x(), canvas_pos.y())
            
            self.graph_manager.update_node_position(self.dragging_node, img_x, img_y)
            self.update()
        elif self.mode == 'add_edge' and self.edge_start_node:
            self.update()
            
    def mouseReleaseEvent(self, event):
        """Handle mouse release events."""
        if event.button() == Qt.MouseButton.MiddleButton or (event.button() == Qt.MouseButton.LeftButton and self.mode == 'pan'):
            self.panning = False
            if self.mode == 'pan':
                self.setCursor(Qt.CursorShape.OpenHandCursor)
            else:
                self.setCursor(Qt.CursorShape.ArrowCursor)
            
        self.dragging_node = None
        
    def get_node_at_position(self, pos):
        """Get the node at the given position."""
        for node_id, node_data in self.graph_manager.nodes.items():
            canvas_pos = self.image_to_canvas(node_data['x'], node_data['y'])
            node_radius = self.get_node_radius(node_id)
            distance = math.sqrt((pos.x() - canvas_pos.x())**2 + (pos.y() - canvas_pos.y())**2)
            if distance <= node_radius + 5:  # Small tolerance
                return node_id
        return None
        
    def get_edge_at_position(self, pos, threshold=10):
        """Get the edge at the given position."""
        for edge in self.graph_manager.edges:
            node1_id, node2_id = edge
            if node1_id not in self.graph_manager.nodes or node2_id not in self.graph_manager.nodes:
                continue
                
            node1 = self.graph_manager.nodes[node1_id]
            node2 = self.graph_manager.nodes[node2_id]
            
            p1 = self.image_to_canvas(node1['x'], node1['y'])
            p2 = self.image_to_canvas(node2['x'], node2['y'])
            
            # Calculate distance from point to line segment
            distance = self.point_to_line_distance(pos, p1, p2)
            if distance <= threshold:
                return edge
        return None
        
    def point_to_line_distance(self, point, line_start, line_end):
        """Calculate the distance from a point to a line segment."""
        line_length_squared = (line_end.x() - line_start.x())**2 + (line_end.y() - line_start.y())**2
        
        if line_length_squared == 0:
            return math.sqrt((point.x() - line_start.x())**2 + (point.y() - line_start.y())**2)
            
        t = max(0, min(1, (
            (point.x() - line_start.x()) * (line_end.x() - line_start.x()) +
            (point.y() - line_start.y()) * (line_end.y() - line_start.y())
        ) / line_length_squared))
        
        projection = QPointF(
            line_start.x() + t * (line_end.x() - line_start.x()),
            line_start.y() + t * (line_end.y() - line_start.y())
        )
        
        return math.sqrt((point.x() - projection.x())**2 + (point.y() - projection.y())**2)
        
    def export_image(self, image_path):
        """Export the full graph overlay on the background image."""
        if not self.background_image or self.background_image.isNull():
            print("✗ No background image to export")
            return False
        
        # Create a pixmap with the original image size
        original_width = self.original_image_size[0]
        original_height = self.original_image_size[1]
        
        pixmap = QPixmap(original_width, original_height)
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Draw the original background image
        painter.drawPixmap(0, 0, self.background_image)
        
        # Draw all edges on the original image coordinates
        for edge in self.graph_manager.edges:
            node1_id, node2_id = edge
            
            if node1_id not in self.graph_manager.nodes or node2_id not in self.graph_manager.nodes:
                continue
                
            node1 = self.graph_manager.nodes[node1_id]
            node2 = self.graph_manager.nodes[node2_id]
            
            # Use original coordinates (no transformation needed)
            pos1 = QPointF(node1['x'], node1['y'])
            pos2 = QPointF(node2['x'], node2['y'])
            
            # Get edge color
            edge_color = self.get_edge_color(node1_id, node2_id)
            painter.setPen(QPen(edge_color, self.edge_width, Qt.PenStyle.SolidLine))
            painter.drawLine(pos1, pos2)
        
        # Draw all nodes on the original image coordinates
        for node_id, node_data in self.graph_manager.nodes.items():
            # Use original coordinates
            pos = QPointF(node_data['x'], node_data['y'])
            
            node_radius = self.get_node_radius(node_id)
            node_color = self.get_node_color(node_id)
            
            painter.setBrush(QBrush(node_color))
            painter.setPen(QPen(QColor(0, 0, 0), 2))
            painter.drawEllipse(pos, node_radius, node_radius)
            
            # Draw node labels (skip for corridor nodes)
            node_type = node_data.get('type', 'unknown').lower()
            if node_type != 'corridor':
                painter.setPen(QPen(QColor(0, 0, 0)))
                painter.setFont(QFont("Arial", 8))
                painter.drawText(
                    QRectF(pos.x() - 50, pos.y() - 35, 100, 20),
                    Qt.AlignmentFlag.AlignCenter,
                    str(node_id)
                )
        
        painter.end()
        
        success = pixmap.save(image_path)
        if success:
            print(f"✓ Exported full overlay image to {image_path}")
        else:
            print(f"✗ Failed to save image to {image_path}")
        return success