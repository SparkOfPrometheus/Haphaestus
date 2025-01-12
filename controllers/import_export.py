import json
from PySide6.QtWidgets import QMessageBox

def export_data(idea_nodes, connections, file_path):
    """
    Export the mind map data to a JSON file.
    
    Args:
        idea_nodes (list): List of IdeaNode objects
        connections (list): List of (source_id, target_id) tuples
        file_path (str): Path to save the JSON file
    """
    try:
        data = {
            "nodes": [],
            "connections": []
        }
        
        # Export nodes
        for node in idea_nodes:
            node_data = {
                "id": node.id,
                "title": node.title,
                "description": node.description,
                "keywords": node.keywords,
                "color": node.color,
                "shape": node.shape_type,
                "image": node.image_path,
                "position": {
                    "x": node.scenePos().x(),
                    "y": node.scenePos().y()
                }
            }
            data["nodes"].append(node_data)
        
        # Export connections
        for source_id, target_id in connections:
            data["connections"].append({
                "source": source_id,
                "target": target_id
            })
        
        # Write to file
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
            
        QMessageBox.information(None, "Export Successful", 
                              f"Mind map exported to:\n{file_path}")
                              
    except Exception as e:
        QMessageBox.critical(None, "Export Error", str(e))
        raise

def import_data(file_path, add_node_callback, add_connection_callback):
    """
    Import mind map data from a JSON file.
    
    Args:
        file_path (str): Path to the JSON file
        add_node_callback (callable): Function to add nodes
        add_connection_callback (callable): Function to add connections
    """
    try:
        # Read and parse JSON
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Validate basic structure
        if not isinstance(data, dict):
            raise ValueError("Invalid file format: root must be an object")
        if "nodes" not in data or "connections" not in data:
            raise ValueError("Invalid file format: missing required sections")
        
        # Import nodes
        for node_data in data.get("nodes", []):
            add_node_callback(node_data)
        
        # Import connections
        for conn_data in data.get("connections", []):
            if not isinstance(conn_data, dict):
                continue
            if "source" not in conn_data or "target" not in conn_data:
                continue
            
            add_connection_callback(conn_data["source"], conn_data["target"])
        
        QMessageBox.information(None, "Import Successful", 
                              f"Mind map imported from:\n{file_path}")
                              
    except Exception as e:
        QMessageBox.critical(None, "Import Error", str(e))
        raise
