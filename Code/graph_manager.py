import json
import os

class GraphManager:
    """Manages graph data (nodes and edges)."""
    
    def __init__(self):
        self.nodes = {}
        self.edges = []
        self.next_node_id = 0
        self.node_id_prefix = "new_node_"  # Prefix for new nodes to avoid conflicts
        
        # Track counts for proper naming
        self.node_type_counters = {
            'room': 0,
            'door': 0,
            'corridor': 0,
            'outside': 0,
            'transition': 0
        }
        
    def update_node_counters(self):
        """Update node type counters based on existing nodes."""
        # Reset counters
        for key in self.node_type_counters:
            self.node_type_counters[key] = 0
        
        # Count existing nodes by type
        for node_id, node_data in self.nodes.items():
            node_type = node_data.get('type', 'unknown').lower()
            
            # Extract number from node_id if it follows the pattern
            if node_type in self.node_type_counters:
                # Try to extract the highest number for each type
                if node_id.startswith(f"{node_type}_"):
                    try:
                        num = int(node_id.split('_')[1])
                        if num >= self.node_type_counters[node_type]:
                            self.node_type_counters[node_type] = num + 1
                    except (IndexError, ValueError):
                        pass
                elif node_id.startswith(f"r2c_door_") or node_id.startswith(f"c2c_door_"):
                    # Handle door naming patterns
                    try:
                        num = int(node_id.split('_')[-1])
                        if num >= self.node_type_counters['door']:
                            self.node_type_counters['door'] = num + 1
                    except (IndexError, ValueError):
                        pass
                elif node_id.startswith(f"corridor_connect_"):
                    # Handle corridor naming patterns
                    try:
                        num = int(node_id.split('_')[-1])
                        if num >= self.node_type_counters['corridor']:
                            self.node_type_counters['corridor'] = num + 1
                    except (IndexError, ValueError):
                        pass
        
    def add_node(self, x, y, node_id=None, **attributes):
        """Add a new node to the graph."""
        if node_id is None:
            # Generate a proper ID based on node type
            node_type = attributes.get('type', 'room').lower()
            
            if node_type in self.node_type_counters:
                counter = self.node_type_counters[node_type]
                
                # Use proper naming convention
                if node_type == 'door':
                    node_id = f"r2c_door_{counter}"
                elif node_type == 'corridor':
                    node_id = f"corridor_connect_{counter}"
                else:
                    node_id = f"{node_type}_{counter}"
                
                self.node_type_counters[node_type] = counter + 1
            else:
                # Fallback for unknown types
                node_id = f"{self.node_id_prefix}{self.next_node_id}"
                self.next_node_id += 1
        else:
            # If node_id is provided, update next_node_id if it's numeric
            if isinstance(node_id, int) and node_id >= self.next_node_id:
                self.next_node_id = node_id + 1
        
        # Always add floor attribute for rooms
        if attributes.get('type', '').lower() == 'room':
            if 'floor' not in attributes:
                attributes['floor'] = 'Ground_Floor'
                
        self.nodes[node_id] = {
            'x': x,
            'y': y,
            **attributes
        }
        print(f"✓ Added node '{node_id}' at ({x:.1f}, {y:.1f}) with type: {attributes.get('type', 'unknown')}")
        return node_id
        
    def remove_node(self, node_id):
        """Remove a node and all connected edges."""
        if node_id in self.nodes:
            del self.nodes[node_id]
            
            # Remove all edges connected to this node
            edges_before = len(self.edges)
            self.edges = [
                edge for edge in self.edges 
                if node_id not in edge
            ]
            edges_removed = edges_before - len(self.edges)
            print(f"✓ Removed node '{node_id}' and {edges_removed} connected edge(s)")
            return True
        else:
            print(f"✗ Cannot remove node '{node_id}': Node does not exist")
            return False
        
    def update_node_position(self, node_id, x, y):
        """Update the position of a node."""
        if node_id in self.nodes:
            self.nodes[node_id]['x'] = x
            self.nodes[node_id]['y'] = y
            return True
        return False
        
    def add_edge(self, node1_id, node2_id, **attributes):
        """Add an edge between two nodes."""
        # Check if both nodes exist
        if node1_id not in self.nodes:
            print(f"✗ Cannot add edge: Node {node1_id} does not exist")
            return False
        if node2_id not in self.nodes:
            print(f"✗ Cannot add edge: Node {node2_id} does not exist")
            return False
            
        edge = (node1_id, node2_id)
        reverse_edge = (node2_id, node1_id)
        
        # Check if edge already exists (in either direction)
        if edge in self.edges or reverse_edge in self.edges:
            print(f"✗ Edge between {node1_id} and {node2_id} already exists")
            return False
            
        self.edges.append(edge)
        print(f"✓ Added edge: {node1_id} → {node2_id}")
        return True
        
    def remove_edge(self, edge):
        """Remove an edge."""
        if edge in self.edges:
            self.edges.remove(edge)
            return True
        # Also check reverse direction
        reverse_edge = (edge[1], edge[0])
        if reverse_edge in self.edges:
            self.edges.remove(reverse_edge)
            return True
        return False
        
    def clear(self):
        """Clear all graph data."""
        self.nodes = {}
        self.edges = []
        self.next_node_id = 0
        
    def load_from_json(self, file_path):
        """Load graph data from a JSON file."""
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
                
            self.clear()
            
            # Load nodes
            if 'nodes' in data:
                for node_data in data['nodes']:
                    # Get node ID - handle both string and integer IDs
                    node_id = node_data.get('id', self.next_node_id)
                    
                    # Handle both position formats:
                    # Format 1: "position": [x, y]
                    # Format 2: "x": value, "y": value
                    if 'position' in node_data and isinstance(node_data['position'], (list, tuple)):
                        x = node_data['position'][0]
                        y = node_data['position'][1]
                    else:
                        x = node_data.get('x', 0)
                        y = node_data.get('y', 0)
                    
                    # Extract other attributes (excluding id, x, y, position)
                    attributes = {k: v for k, v in node_data.items() 
                                if k not in ['id', 'x', 'y', 'position']}
                    
                    self.add_node(x, y, node_id, **attributes)
                    
            # Load edges
            if 'edges' in data:
                for edge_data in data['edges']:
                    if isinstance(edge_data, dict):
                        source = edge_data.get('source')
                        target = edge_data.get('target')
                    elif isinstance(edge_data, (list, tuple)) and len(edge_data) >= 2:
                        source = edge_data[0]
                        target = edge_data[1]
                    else:
                        continue
                        
                    if source is not None and target is not None:
                        self.add_edge(source, target)
            
            # Update node counters after loading to ensure new nodes get correct IDs
            self.update_node_counters()
                        
            print(f"✓ Loaded {len(self.nodes)} nodes and {len(self.edges)} edges")
            print(f"✓ Node counters: {self.node_type_counters}")
            return True
        except Exception as e:
            print(f"✗ Error loading JSON: {e}")
            import traceback
            traceback.print_exc()
            return False
            
    def save_to_json(self, file_path):
        """Save graph data to a JSON file."""
        try:
            # Prepare data
            data = {
                'nodes': [],
                'edges': []
            }
            
            # Add nodes with proper formatting
            for node_id, node_data in self.nodes.items():
                # Create a copy to avoid modifying original
                node_export = {
                    'id': node_id,
                }
                
                # Add type first if it exists
                if 'type' in node_data:
                    node_export['type'] = node_data['type']
                
                # Add position as array [x, y]
                node_export['position'] = [node_data['x'], node_data['y']]
                
                # Add floor if it exists (important for rooms)
                if 'floor' in node_data:
                    node_export['floor'] = node_data['floor']
                
                # Add any other attributes (excluding x, y which are now in position)
                for key, value in node_data.items():
                    if key not in ['x', 'y', 'type', 'floor', 'position']:
                        node_export[key] = value
                
                data['nodes'].append(node_export)
                
            # Add edges
            for edge in self.edges:
                edge_export = {
                    'source': edge[0],
                    'target': edge[1]
                }
                data['edges'].append(edge_export)
                
            # Write to file
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2)
                
            print(f"✓ Saved {len(self.nodes)} nodes and {len(self.edges)} edges to {file_path}")
            return True
        except Exception as e:
            print(f"✗ Error saving JSON: {e}")
            import traceback
            traceback.print_exc()
            return False
            
    def get_node_count(self):
        """Get the number of nodes."""
        return len(self.nodes)
        
    def get_edge_count(self):
        """Get the number of edges."""
        return len(self.edges)
        
    def get_graph_stats(self):
        """Get statistics about the graph."""
        return {
            'node_count': self.get_node_count(),
            'edge_count': self.get_edge_count(),
            'next_node_id': self.next_node_id
        }