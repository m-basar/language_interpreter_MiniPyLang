"""
environment.py - Complete Stage 6 variable storage system

Provides variable storage and management for MiniPyLang:
- Variable definition and lookup
- Variable deletion
- Error handling for undefined variables
- Debugging and analysis capabilities
- Compatible with control flow constructs
"""


class EnvironmentError(Exception):
    """Exception for environment-related errors"""
    def __init__(self, message, variable_name=None):
        self.message = message
        self.variable_name = variable_name
        super().__init__(message)


class Environment:
    """
    Variable storage environment for MiniPyLang.
    
    Manages variable storage with proper error handling and
    debugging capabilities. Works seamlessly with control flow.
    """
    
    def __init__(self):
        """Initialise empty environment"""
        self._variables = {}
        
        # Optional: tracking for debugging and analysis
        self._access_history = []
        self._creation_order = []
        self._deletion_count = 0
    
    def define(self, name, value):
        """
        Define or redefine a variable.
        
        Args:
            name (str): Variable name
            value: Variable value (MiniPyValue instance)
        
        Returns:
            The stored value
        """
        was_defined = name in self._variables
        old_value = self._variables.get(name)
        
        # Store the value
        self._variables[name] = value
        
        # Track creation order for new variables
        if not was_defined:
            self._creation_order.append(name)
        
        # Log operation for debugging
        operation = 'redefine' if was_defined else 'define'
        self._access_history.append((operation, name, old_value, value))
        
        return value
    
    def get(self, name):
        """
        Get variable value.
        
        Args:
            name (str): Variable name
        
        Returns:
            Variable value
        
        Raises:
            EnvironmentError: If variable is undefined
        """
        if name not in self._variables:
            # Provide helpful suggestions for similar names
            similar_names = [var for var in self._variables.keys() 
                           if self._similarity_score(var, name) > 0.6]
            
            error_msg = f"Undefined variable '{name}'"
            if similar_names:
                error_msg += f". Did you mean: {', '.join(similar_names)}?"
            
            raise EnvironmentError(error_msg, name)
        
        value = self._variables[name]
        self._access_history.append(('get', name, value, None))
        
        return value
    
    def delete(self, name):
        """
        Delete a variable.
        
        Args:
            name (str): Variable name
        
        Returns:
            The deleted value
        
        Raises:
            EnvironmentError: If variable is undefined
        """
        if name not in self._variables:
            raise EnvironmentError(f"Cannot delete undefined variable '{name}'", name)
        
        deleted_value = self._variables[name]
        del self._variables[name]
        
        # Remove from creation order tracking
        if name in self._creation_order:
            self._creation_order.remove(name)
        
        # Track deletion
        self._access_history.append(('delete', name, deleted_value, None))
        self._deletion_count += 1
        
        return deleted_value
    
    def is_defined(self, name):
        """
        Check if variable exists.
        
        Args:
            name (str): Variable name
        
        Returns:
            bool: True if variable exists
        """
        return name in self._variables
    
    def get_all_variables(self):
        """
        Get all variables as Python dict.
        
        Returns:
            dict: All variables with their Python values
        """
        result = {}
        for name, value in self._variables.items():
            if hasattr(value, 'to_python_value'):
                result[name] = value.to_python_value()
            else:
                result[name] = value
        return result
    
    def clear(self):
        """Clear all variables"""
        cleared_variables = dict(self._variables)
        self._variables.clear()
        self._creation_order.clear()
        
        # Log the clear operation
        self._access_history.append(('clear_all', None, cleared_variables, None))
    
    def get_statistics(self):
        """
        Get environment statistics for debugging.
        
        Returns:
            dict: Statistics about variable usage
        """
        return {
            'total_variables': len(self._variables),
            'total_operations': len(self._access_history),
            'deletions': self._deletion_count,
            'variable_types': {
                name: type(value).__name__ 
                for name, value in self._variables.items()
            },
            'creation_order': list(self._creation_order)
        }
    
    def _similarity_score(self, str1, str2):
        """Calculate similarity score for helpful error messages"""
        if len(str1) == 0 or len(str2) == 0:
            return 0
        
        # Simple similarity based on common characters
        common = set(str1.lower()) & set(str2.lower())
        total = set(str1.lower()) | set(str2.lower())
        
        return len(common) / len(total) if total else 0
    
    def __str__(self):
        """String representation for debugging"""
        if not self._variables:
            return "Environment: (empty)"
        
        var_strings = []
        for name in self._creation_order:
            if name in self._variables:
                value = self._variables[name]
                if hasattr(value, 'is_string') and hasattr(value, 'value') and value.is_string():
                    var_strings.append(f"{name} = \"{value.value}\"")
                else:
                    var_strings.append(f"{name} = {value}")
        
        return "Environment: " + ", ".join(var_strings)