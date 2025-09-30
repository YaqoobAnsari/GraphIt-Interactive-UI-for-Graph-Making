"""
Graph Editor Application
========================
A powerful UI-based graph editor for overlay visualization on floor plans.

This application allows users to:
- Load graph data from JSON files
- Overlay graphs on floor plan images
- Add, remove, and modify nodes and edges interactively
- Export edited graphs and rendered images

Author: Graph Editor Team
Version: 1.0.0
"""

import sys
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QFont

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'Code'))

from Code.graph_editor_ui import GraphEditorUI

def setup_application():
    """Configure the QApplication with global settings."""
    app = QApplication(sys.argv)
    
    # Set application metadata
    app.setApplicationName("Graph Editor")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("Graph Tools")
    
    # Use Fusion style for modern look
    app.setStyle('Fusion')
    
    # Set default font
    font = QFont("Segoe UI", 10)
    app.setFont(font)
    
    return app


def ensure_directories():
    """Ensure all required directories exist."""
    required_dirs = [
        'Inputs/Jsons',
        'Inputs/Plans',
        'Results/Jsons',
        'Results/Images',
        'Code'
    ]
    
    for directory in required_dirs:
        os.makedirs(directory, exist_ok=True)
        
    print("✓ Directory structure verified")


def main():
    """Main entry point for the Graph Editor application."""
    try:
        # Ensure directory structure exists
        ensure_directories()
        
        # Setup and configure application
        app = setup_application()
        
        # Create and show main window
        editor = GraphEditorUI()
        editor.show()
        
        print("✓ Graph Editor launched successfully")
        print("=" * 50)
        print("Welcome to Graph Editor!")
        print("Load a JSON and Image to get started.")
        print("=" * 50)
        
        # Start event loop
        sys.exit(app.exec())
        
    except Exception as e:
        print(f"✗ Error launching application: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()