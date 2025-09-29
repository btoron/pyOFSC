"""
Schema-Model Mapper Utility

This module provides functionality to map Swagger JSON schema names to corresponding
Pydantic model classes in the OFSC Python Wrapper.
"""

import inspect
from typing import Dict, Type, Optional, List, Any
from pydantic import BaseModel

from ofsc.models import core, metadata, capacity, auth, base
from ofsc.models.base import BaseOFSResponse


class SchemaModelMapper:
    """Maps Swagger schema names to Pydantic model classes."""

    # Explicit overrides for schemas that don't follow naming conventions
    SCHEMA_TO_MODEL_OVERRIDES: Dict[str, str] = {
        # Add explicit mappings for edge cases
        # Format: "SwaggerSchemaName": "PydanticModelClassName"
    }

    def __init__(self):
        """Initialize the mapper and discover all available model classes."""
        self._model_classes_cache: Optional[Dict[str, Type[BaseModel]]] = None
        self._schema_to_model_cache: Dict[str, Optional[Type[BaseModel]]] = {}

    def get_model_class_by_schema_name(
        self, schema_name: str
    ) -> Optional[Type[BaseModel]]:
        """
        Get the Pydantic model class corresponding to a Swagger schema name.

        Args:
            schema_name: The name of the schema from swagger.json (e.g., 'ActivityTypeGroups')

        Returns:
            The corresponding Pydantic model class, or None if not found
        """
        # Check cache first
        if schema_name in self._schema_to_model_cache:
            return self._schema_to_model_cache[schema_name]

        # Check explicit overrides first
        if schema_name in self.SCHEMA_TO_MODEL_OVERRIDES:
            override_name = self.SCHEMA_TO_MODEL_OVERRIDES[schema_name]
            model_class = self._find_model_by_name(override_name)
            self._schema_to_model_cache[schema_name] = model_class
            return model_class

        # Try direct naming convention (most common case)
        model_class = self._find_model_by_name(schema_name)
        if model_class:
            self._schema_to_model_cache[schema_name] = model_class
            return model_class

        # Try common variations
        variations = self._generate_name_variations(schema_name)
        for variation in variations:
            model_class = self._find_model_by_name(variation)
            if model_class:
                self._schema_to_model_cache[schema_name] = model_class
                return model_class

        # Not found
        self._schema_to_model_cache[schema_name] = None
        return None

    def discover_model_classes(self) -> Dict[str, Type[BaseModel]]:
        """
        Discover all Pydantic model classes in the ofsc.models package.

        Returns:
            Dictionary mapping class names to model classes
        """
        if self._model_classes_cache is not None:
            return self._model_classes_cache

        model_classes = {}

        # Scan all model modules
        modules_to_scan = [core, metadata, capacity, auth, base]

        for module in modules_to_scan:
            for name, obj in inspect.getmembers(module, inspect.isclass):
                # Check if it's a Pydantic model (inherits from BaseModel)
                if (
                    issubclass(obj, BaseModel)
                    and obj.__module__ == module.__name__  # Defined in this module
                    and obj != BaseModel  # Not the base class itself
                    and obj != BaseOFSResponse
                ):  # Not the base response class
                    model_classes[name] = obj

        self._model_classes_cache = model_classes
        return model_classes

    def get_all_mapped_schemas(self) -> Dict[str, Type[BaseModel]]:
        """
        Get all schemas that have corresponding model classes.

        Returns:
            Dictionary mapping schema names to model classes
        """
        model_classes = self.discover_model_classes()
        mapped_schemas = {}

        # Try to map each model class back to potential schema names
        for class_name, model_class in model_classes.items():
            # Direct mapping
            mapped_schemas[class_name] = model_class

            # Check if this model is an override target
            for schema_name, override_name in self.SCHEMA_TO_MODEL_OVERRIDES.items():
                if override_name == class_name:
                    mapped_schemas[schema_name] = model_class

        return mapped_schemas

    def get_unmapped_schemas(self, schema_names: List[str]) -> List[str]:
        """
        Get list of schema names that don't have corresponding model classes.

        Args:
            schema_names: List of schema names from swagger.json

        Returns:
            List of unmapped schema names
        """
        unmapped = []
        for schema_name in schema_names:
            if self.get_model_class_by_schema_name(schema_name) is None:
                unmapped.append(schema_name)
        return unmapped

    def get_orphaned_models(self, schema_names: List[str]) -> List[str]:
        """
        Get list of model classes that don't correspond to any swagger schema.

        Args:
            schema_names: List of schema names from swagger.json

        Returns:
            List of model class names without corresponding schemas
        """
        model_classes = self.discover_model_classes()
        schema_set = set(schema_names)

        # Add override targets to schema set
        for override_name in self.SCHEMA_TO_MODEL_OVERRIDES.values():
            schema_set.add(override_name)

        orphaned = []
        for class_name in model_classes.keys():
            # Check if this class name or any of its variations match a schema
            found_match = False
            variations = self._generate_name_variations(class_name)
            for variation in [class_name] + variations:
                if variation in schema_set:
                    found_match = True
                    break

            if not found_match:
                orphaned.append(class_name)

        return orphaned

    def _find_model_by_name(self, name: str) -> Optional[Type[BaseModel]]:
        """Find a model class by exact name match."""
        model_classes = self.discover_model_classes()
        return model_classes.get(name)

    def _generate_name_variations(self, name: str) -> List[str]:
        """
        Generate common naming variations for a schema/model name.

        Args:
            name: The original name

        Returns:
            List of potential variations
        """
        variations = []

        # Singular/plural variations
        if name.endswith("s") and len(name) > 1:
            # Try removing 's' for plural -> singular
            variations.append(name[:-1])
        else:
            # Try adding 's' for singular -> plural
            variations.append(name + "s")

        # Common suffixes/prefixes
        variations.extend(
            [
                f"{name}Response",
                f"{name}Request",
                f"{name}List",
                f"{name}Collection",
                name.replace("Response", ""),
                name.replace("Request", ""),
                name.replace("List", ""),
                name.replace("Collection", ""),
            ]
        )

        # Remove duplicates and original name
        variations = list(set(variations))
        if name in variations:
            variations.remove(name)

        return variations

    def generate_mapping_report(self, schema_names: List[str]) -> Dict[str, Any]:
        """
        Generate a comprehensive mapping report.

        Args:
            schema_names: List of schema names from swagger.json

        Returns:
            Dictionary with mapping statistics and details
        """
        mapped_schemas = []
        unmapped_schemas = self.get_unmapped_schemas(schema_names)
        orphaned_models = self.get_orphaned_models(schema_names)

        for schema_name in schema_names:
            model_class = self.get_model_class_by_schema_name(schema_name)
            if model_class:
                mapped_schemas.append(
                    {
                        "schema_name": schema_name,
                        "model_class": model_class.__name__,
                        "module": model_class.__module__,
                    }
                )

        return {
            "total_schemas": len(schema_names),
            "mapped_count": len(mapped_schemas),
            "unmapped_count": len(unmapped_schemas),
            "orphaned_count": len(orphaned_models),
            "mapping_coverage": len(mapped_schemas) / len(schema_names)
            if schema_names
            else 0,
            "mapped_schemas": mapped_schemas,
            "unmapped_schemas": unmapped_schemas,
            "orphaned_models": orphaned_models,
        }
