"""
Enhanced environment.py - Addressing data persistence requirements

This enhanced version provides support for None/nil values and variable
deletion along with more sophisticated memory management capabilities.
"""


class EnvironmentError(Exception):
    """Enhanced exception for environment-related errors"""
    def __init__(self, message, variable_name=None):
        self.message = message
        self.variable_name = variable_name
        super().__init__(message)


class Environment:
    """
    Enhanced environment data persistence.
    
    This version provides explicit support for variable deletion and None/nil
    values.
    """
    
    def __init__(self):
        """Initialise environment with enhanced tracking capabilities"""
        self._variables = {}
        
        # Enhanced tracking for debugging and analysis
        self._access_history = []
        self._deletion_history = []
        
        # Track variable creation order for debugging
        self._creation_order = []
    
    def define(self, name, value):
        """
        Define or redefine a variable with enhanced persistence tracking.
        
        This method tracks variable lifecycle more carefully.
        """
        was_defined = name in self._variables
        old_value = self._variables.get(name)
        
        self._variables[name] = value
        
        # Track creation order for new variables
        if not was_defined:
            self._creation_order.append(name)
        
        # Log the operation for debugging
        operation = 'redefine' if was_defined else 'define'
        self._access_history.append((operation, name, old_value, value))
        
        return value
    
    def get(self, name):
        """
        Enhanced variable lookup with better error handling.
        
        This method provides more informative error messages and
        tracks access patterns for debugging purposes.
        """
        if name not in self._variables:
            # Provide helpful suggestions for similar variable names
            similar_names = [var for var in self._variables.keys() 
                           if abs(len(var) - len(name)) <= 2]
            
            error_msg = f"Undefined variable '{name}'"
            if similar_names:
                error_msg += f". Did you mean one of: {', '.join(similar_names)}?"
            
            raise EnvironmentError(error_msg, name)
        
        value = self._variables[name]
        self._access_history.append(('get', name, value, None))
        
        return value
    
    def delete(self, name):
        """
        Delete a variable from the environment.
        
        This method implements explicit variable deletion.
        """
        if name not in self._variables:
            raise EnvironmentError(f"Cannot delete undefined variable '{name}'", name)
        
        deleted_value = self._variables[name]
        del self._variables[name]
        
        # Remove from creation order tracking
        if name in self._creation_order:
            self._creation_order.remove(name)
        
        # Track deletion for debugging
        self._deletion_history.append((name, deleted_value))
        self._access_history.append(('delete', name, deleted_value, None))
        
        return deleted_value
    
    def is_defined(self, name):
        """
        Enhanced existence checking.
        
        This method helps the interpreter determine variable existence
        more reliably, supporting the data persistence requirements.
        """
        return name in self._variables
    
    def get_all_variables(self):
        """
        Return all defined variables with enhanced type information.
        
        This method now provides more detailed information about
        stored values, helping with debugging and analysis.
        """
        result = {}
        for name, value in self._variables.items():
            if hasattr(value, 'to_python_value'):
                result[name] = value.to_python_value()
            else:
                result[name] = value
        return result
    
    def get_variable_info(self, name):
        """
        Get detailed information about a specific variable.
        
        This method provides comprehensive information about variable
        state, type, and history for debugging purposes.
        """
        if name not in self._variables:
            raise EnvironmentError(f"Variable '{name}' is not defined", name)
        
        value = self._variables[name]
        
        # Collect access history for this variable
        variable_history = [entry for entry in self._access_history 
                          if entry[1] == name]
        
        return {
            'name': name,
            'value': value.to_python_value() if hasattr(value, 'to_python_value') else value,
            'type': type(value).__name__,
            'access_count': len([h for h in variable_history if h[0] == 'get']),
            'modification_count': len([h for h in variable_history if h[0] in ['define', 'redefine']]),
            'creation_order': self._creation_order.index(name) if name in self._creation_order else -1
        }
    
    def clear(self):
        """
        Clear all variables with enhanced cleanup tracking.
        
        This method provides complete environment reset while
        maintaining historical information for debugging.
        """
        cleared_variables = dict(self._variables)
        self._variables.clear()
        self._creation_order.clear()
        
        # Log the clear operation
        self._access_history.append(('clear_all', None, cleared_variables, None))
    
    def get_statistics(self):
        """
        Get comprehensive environment statistics.
        
        This method provides insights into variable usage patterns
        and memory utilisation for analysis and optimisation.
        """
        return {
            'total_variables': len(self._variables),
            'total_operations': len(self._access_history),
            'deletions': len(self._deletion_history),
            'variable_types': {
                name: type(value).__name__ 
                for name, value in self._variables.items()
            },
            'creation_order': list(self._creation_order)
        }
    
    def __str__(self):
        """Enhanced string representation with type information"""
        if not self._variables:
            return "Environment: (empty)"
        
        var_strings = []
        for name in self._creation_order:
            if name in self._variables:
                value = self._variables[name]
                if hasattr(value, 'is_string') and value.is_string():
                    var_strings.append(f"{name} = \"{value}\"")
                else:
                    var_strings.append(f"{name} = {value}")
        
        return "Environment: " + ", ".join(var_strings)