"""
environment.py - Variable storage and scope management for MiniPyLang

The environment represents the programme's memory - the association between
variable names and their values. This concept becomes more sophisticated
as we add features like functions and local scopes in later stages.
"""

class EnvironmentError(Exception):
    """Custom exception for environment-related errors"""
    def __init__(self, message, variable_name=None):
        self.message = message
        self.variable_name = variable_name
        super().__init__(message)

class Environment:
    """
    Global variable storage for MiniPyLang.

    The environment maintains the programme's state by storing variable values.
    This design supports the dynamic typing philosophy of MiniPyLang, where
    variables can be reassigned to different types.
    """

    def __init__(self):
        """
        Initialise an empty environment.

        We use a dictionary to map variable names to values, which provides
        efficient lookup and modification operations.
        """
        self._variables = {}
        
        # Track variable access for debugging and optimisation
        self._access_history = []

    def define(self, name, value):
        """
        Define or redefine a variable with a new value.

        MiniPyLang follows dynamic typing principles, allowing variables
        to be reassigned to different types. This provides flexibility
        but requires careful error handling.

        Args:
            name: The variable name (string)
            value: The value to assign (any type)
        """
        old_value = self._variables.get(name)
        self._variables[name] = value
        
        # Log the assignment for debugging
        self._access_history.append(('define', name, old_value, value))
        
        return value

    def get(self, name):
        """
        Retrieve a variable's current value.

        This method implements variable lookup with clear error reporting
        for undefined variables, helping catch typos and logic errors.

        Args:
            name: The variable name to look up

        Returns:
            The current value of the variable

        Raises:
            EnvironmentError: If the variable hasn't been defined
        """
        if name not in self._variables:
            raise EnvironmentError(f"Undefined variable '{name}'", name)
        
        value = self._variables[name]
        self._access_history.append(('get', name, value, None))
        
        return value

    def is_defined(self, name):
        """
        Check if a variable is currently defined.

        This method helps distinguish between undefined variables and
        variables that are defined but have None values.
        """
        return name in self._variables

    def get_all_variables(self):
        """
        Return a copy of all defined variables.

        This method is useful for debugging and for implementing
        features that need to inspect the current programme state.
        """
        return dict(self._variables)

    def clear(self):
        """
        Clear all variables from the environment.

        This method is useful for testing and for implementing
        features like function scopes in later stages.
        """
        self._variables.clear()
        self._access_history.clear()

    def get_access_history(self):
        """
        Return the history of variable accesses for debugging.

        This information can be valuable for understanding programme
        execution and for implementing optimisation features.
        """
        return list(self._access_history)

    def __str__(self):
        """String representation for debugging"""
        if not self._variables:
            return "Environment: (empty)"

        var_strings = []
        for name, value in self._variables.items():
            if isinstance(value, str):
                var_strings.append(f"{name} = \"{value}\"")
            else:
                var_strings.append(f"{name} = {value}")

        return "Environment: " + ", ".join(var_strings)
