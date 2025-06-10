"""
Parameter Reference Utility for Synth Modules.

Defines ParamRef, a helper for symbolic modulation routing.

Author: Valerio Poggi - 2025
"""


class ParamRef:
    """
    A reference to a named parameter of a module,
    used for routing modulation signals.
    """

    def __init__(self, module, name):
        """
        Parameters:
            module (object): The target module.
            name (str): Name of the parameter (e.g., "freq").
        """
        self.module = module
        self.name = name

