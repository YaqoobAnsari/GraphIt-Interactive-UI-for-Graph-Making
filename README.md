# Graph Editor - Interactive Network Overlay Tool

A professional PyQt6-based graph editor for visualizing and editing network graphs overlaid on floor plans. Built for precision editing of spatial graphs with support for multiple node types, continuous edge creation, and high-resolution export.

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![PyQt6](https://img.shields.io/badge/PyQt6-6.4+-green.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

## Features

### Core Functionality
- **Multi-layer visualization**: Overlay graph networks on floor plan images with proper coordinate transformation
- **Type-based rendering**: Distinct colors and sizes for rooms, doors, corridors, transitions, and outdoor nodes
- **Smart node naming**: Automatic sequential naming (e.g., `room_34`, `r2c_door_12`) that continues from existing nodes
- **Continuous edge creation**: Chain multiple edges in sequence without mode switching
- **Real-time manipulation**: Pan, zoom (0.1x-5.0x), and edit with instant visual feedback

### Editing Tools
- **Pan Mode**: Navigate large floor plans with left-click drag or middle-mouse
- **Select Mode**: Click nodes/edges to select, drag nodes to reposition
- **Add Node**: Place nodes with type selection (room/door/corridor/outside/transition)
- **Add Edge**: Continuous edge creation - click nodes sequentially to build paths
- **Delete Operations**: Remove individual nodes or edges

### Visual Enhancements
- **Type-based coloring**: Automatic node colors based on type
- **Type-based glows**: Unique glow colors for selected nodes by type
- **Configurable sizes**: Real-time sliders for node sizes (2-20px) and edge width (1-10px)
- **Grid overlay**: Optional snap-to-grid with adjustable spacing (10-100px)
- **Interactive legend**: Always-visible type reference

### Import/Export
- **JSON Format**: Supports both `"position": [x, y]` and separate `x, y` fields
- **String/Integer IDs**: Handles mixed ID types from existing datasets
- **High-resolution export**: Full floor plan with overlay at original resolution
- **Metadata preservation**: Maintains all node attributes including floor designation

## Installation

### Requirements
- Python 3.8 or higher
- PyQt6 6.4 or higher

### Setup
```bash
# Clone the repository
git clone https://github.com/yourusername/graph-editor.git
cd graph-editor

# Install dependencies
pip install PyQt6

# Run the application
python main.py
```

## Project Structure

```
graph-editor/
├── main.py                      # Application entry point
├── Code/
│   ├── __init__.py             # Package initialization
│   ├── graph_editor_ui.py      # Main window and UI controls
│   ├── canvas.py               # Canvas rendering and interaction
│   └── graph_manager.py        # Graph data structures and I/O
├── Inputs/
│   ├── Jsons/                  # Input graph JSON files
│   └── Plans/                  # Floor plan images (PNG, JPG)
├── Results/
│   ├── Jsons/                  # Exported graph JSON files
│   └── Images/                 # Exported overlay images
└── requirements.txt
```

## Usage

### Basic Workflow

1. **Load Data**
   ```
   File → Load JSON (select your graph file)
   File → Load Image (select your floor plan)
   ```

2. **Navigate**
   - Use Pan mode or middle-mouse to move around
   - Scroll mouse wheel to zoom in/out
   - Grid overlay helps with alignment

3. **Edit Graph**
   - Select node type from left panel
   - Click Add Node mode and place nodes
   - Switch to Add Edge mode
   - Click nodes sequentially to create edges
   - Right-click to exit edge creation mode

4. **Export Results**
   ```
   File → Export
   - JSON: Results/Jsons/[filename]_edited.json
   - Image: Results/Images/[filename]_overlay.png
   ```

### JSON Format

Input format (both styles supported):
```json
{
  "nodes": [
    {
      "id": "room_30",
      "type": "room",
      "position": [680.5, 1299.5],
      "floor": "Ground_Floor"
    }
  ],
  "edges": [
    {
      "source": "room_30",
      "target": "corridor_connect_908"
    }
  ]
}
```

Output format:
```json
{
  "nodes": [
    {
      "id": "room_34",
      "type": "room",
      "position": [1234.5, 567.8],
      "floor": "Ground_Floor"
    }
  ],
  "edges": [
    {
      "source": "room_34",
      "target": "r2c_door_12"
    }
  ]
}
```

### Node Types

| Type | ID Pattern | Color | Default Size | Usage |
|------|-----------|-------|--------------|-------|
| Room | `room_N` | Orange | 8px | Room nodes with floor designation |
| Door | `r2c_door_N` | Green | 8px | Door connections |
| Corridor | `corridor_connect_N` | Magenta | 4px | Corridor waypoints (labels hidden) |
| Transition | `transition_N` | Red | 9px | Transition points between areas |
| Outside | `outside_N` | Crimson | 8px | Exterior nodes |

## Keyboard & Mouse Controls

### Mouse
- **Left Click**: Select/interact (mode-dependent)
- **Left Drag** (Pan mode): Move viewport
- **Left Drag** (Select mode): Move nodes
- **Middle Click + Drag**: Pan in any mode
- **Right Click** (Add Edge mode): Exit to Select mode
- **Scroll Wheel**: Zoom in/out

### Modes
- **Pan**: Navigate the canvas
- **Select**: Select and move nodes/edges
- **Add Node**: Place new nodes (select type first)
- **Add Edge**: Create edges by clicking nodes sequentially
- **Delete Node**: Remove nodes and connected edges
- **Delete Edge**: Remove individual edges

## Advanced Features

### Continuous Edge Creation
When in Add Edge mode:
1. Click first node (highlighted in blue)
2. Click second node (edge created, second node becomes new start)
3. Click third node (edge created from second to third)
4. Continue clicking to chain edges
5. Right-click to exit mode

This enables rapid creation of long paths without mode switching.

### Automatic Node Naming
The system analyzes existing nodes on load:
- Counts highest number for each node type
- New nodes continue the sequence
- Example: If `room_0` to `room_33` exist, next room is `room_34`

### Export Quality
- Image export renders at original floor plan resolution
- No canvas UI elements included
- Nodes and edges drawn at actual coordinates
- Suitable for documentation and analysis

## Troubleshooting

### Issue: Graph not visible after loading
**Solution**: Zoom out with mouse wheel - graph may be at different scale than canvas view

### Issue: Cannot create edge between new nodes
**Solution**: Check console output for detailed error messages. Ensure both nodes exist and edge doesn't already exist.

### Issue: Node IDs not sequential after export
**Solution**: Node counters update on JSON load. Reload the edited JSON to reset counters.

## Development

### Architecture
- **Model**: `graph_manager.py` handles all data operations
- **View**: `canvas.py` manages rendering and transformations
- **Controller**: `graph_editor_ui.py` coordinates UI and interactions

### Extending
To add new node types:
1. Add type to `node_type_counters` in `graph_manager.py`
2. Define color in `node_colors` dict in `canvas.py`
3. Add glow color in `glow_colors` dict
4. Update legend in `draw_legend()` method

## Performance

- Handles 500+ nodes smoothly
- Tested with 1000+ edges
- Supports floor plans up to 4000x4000px
- Real-time rendering during pan/zoom

## License

MIT License - see LICENSE file for details

## Contributing

Contributions welcome. Please:
1. Fork the repository
2. Create a feature branch
3. Submit a pull request with clear description

## Citation

If you use this tool in research, please cite:
```
@software{graph_editor,
  title = {Graph Editor: Interactive Network Overlay Tool},
  author = {Your Name},
  year = {2025},
  url = {https://github.com/yourusername/graph-editor}
}
```

## Acknowledgments

Built with PyQt6 for cross-platform compatibility and professional UI rendering.

---

**Version**: 2.0.0  
**Status**: Production Ready  
**Python**: 3.8+  
**Platform**: Windows, macOS, Linux
