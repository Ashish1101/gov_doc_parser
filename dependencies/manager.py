from typing import Dict, Any, Type, Union
from pydantic import BaseModel, ValidationError
from config.base import DependencyConfig

class DependencyManager:
    def __init__(self, dependency_configs: Dict[str, Any]):
        self.dependency_configs = dependency_configs
        self.is_json_schema = isinstance(dependency_configs, dict) and 'properties' in dependency_configs
        
    def validate_dependencies(self, dependencies: Dict[str, Any]) -> Dict[str, Any]:
        """Validate provided dependencies against configuration"""
        if self.is_json_schema:
            return self._validate_json_schema_dependencies(dependencies)
        else:
            return self._validate_config_dependencies(dependencies)

    def _validate_json_schema_dependencies(self, dependencies: Dict[str, Any]) -> Dict[str, Any]:
        """Validate dependencies against JSON schema"""
        validated_deps = {}
        properties = self.dependency_configs.get('properties', {})
        required_fields = self.dependency_configs.get('required', [])
        
        for field_name, field_schema in properties.items():
            # Check if required field is missing
            if field_name in required_fields and field_name not in dependencies:
                raise ValueError(f"Required field '{field_name}' not provided")
                
            if field_name in dependencies:
                value = dependencies[field_name]
                # Basic type validation based on schema
                field_type = field_schema.get('type')
                if field_type == 'string' and not isinstance(value, str):
                    raise TypeError(f"Field '{field_name}' should be a string")
                elif field_type == 'number' and not isinstance(value, (int, float)):
                    raise TypeError(f"Field '{field_name}' should be a number")
                # Add more type validations as needed
                
                validated_deps[field_name] = value
                
        return validated_deps

    def _validate_config_dependencies(self, dependencies: Dict[str, Any]) -> Dict[str, Any]:
        """Validate dependencies against DependencyConfig"""
        validated_deps = {}
        
        for dep_name, dep_config in self.dependency_configs.items():
            if dep_name not in dependencies and dep_config.required:
                raise ValueError(f"Required dependency '{dep_name}' not provided")
                
            if dep_name in dependencies:
                value = dependencies[dep_name]
                if not dep_config.validate_type(value):
                    type_name = getattr(dep_config.type, '__name__', str(dep_config.type))
                    raise TypeError(
                        f"Dependency '{dep_name}' should be of type {type_name}"
                    )
                validated_deps[dep_name] = value
                
        return validated_deps 