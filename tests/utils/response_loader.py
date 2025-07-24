"""Response loader utility for test data."""

import json
from pathlib import Path
from typing import Any, Dict, Optional


class ResponseLoader:
    """Utility class for loading and processing API response examples."""
    
    def __init__(self, response_dir: Path):
        """Initialize with the response examples directory.
        
        Args:
            response_dir: Path to the directory containing response examples
        """
        self.response_dir = Path(response_dir)
        if not self.response_dir.exists():
            raise ValueError(f"Response directory does not exist: {response_dir}")
    
    def load_response(self, filename: str) -> Dict[str, Any]:
        """Load a JSON response file.
        
        Args:
            filename: Name of the JSON file to load
            
        Returns:
            The parsed JSON data
            
        Raises:
            FileNotFoundError: If the file doesn't exist
            json.JSONDecodeError: If the file isn't valid JSON
        """
        file_path = self.response_dir / filename
        if not file_path.exists():
            raise FileNotFoundError(f"Response file not found: {file_path}")
            
        with open(file_path, "r") as f:
            return json.load(f)
    
    def load_response_without_metadata(self, filename: str) -> Dict[str, Any]:
        """Load a JSON response file and remove _metadata field.
        
        Args:
            filename: Name of the JSON file to load
            
        Returns:
            The parsed JSON data without _metadata field
        """
        data = self.load_response(filename)
        if "_metadata" in data:
            del data["_metadata"]
        return data
    
    def load_items_from_response(self, filename: str, items_key: str = "items") -> list:
        """Load items from a list response.
        
        Args:
            filename: Name of the JSON file to load
            items_key: Key containing the list of items (default: "items")
            
        Returns:
            List of items from the response
        """
        data = self.load_response_without_metadata(filename)
        return data.get(items_key, [])
    
    def get_first_item(self, filename: str, items_key: str = "items") -> Optional[Dict[str, Any]]:
        """Get the first item from a list response.
        
        Args:
            filename: Name of the JSON file to load
            items_key: Key containing the list of items (default: "items")
            
        Returns:
            First item from the list or None if empty
        """
        items = self.load_items_from_response(filename, items_key)
        return items[0] if items else None
    
    def list_available_responses(self, pattern: str = "*.json") -> list[str]:
        """List all available response files matching a pattern.
        
        Args:
            pattern: Glob pattern to match files (default: "*.json")
            
        Returns:
            List of matching filenames
        """
        return sorted([f.name for f in self.response_dir.glob(pattern)])