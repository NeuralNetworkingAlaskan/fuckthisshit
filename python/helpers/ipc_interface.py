from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Callable, Union, TypeVar, Awaitable

T = TypeVar('T')

class AbstractAgentZeroIPC(ABC):
    """Abstract interface for Agent Zero inter-process communication"""
    
    @abstractmethod
    async def call_development_function(self, func: Union[Callable[..., T], Callable[..., Awaitable[T]]], *args, **kwargs) -> T:
        """Call a development function remotely or locally
        
        Args:
            func: The function to call
            *args: Positional arguments for the function
            **kwargs: Keyword arguments for the function
            
        Returns:
            The result of the function call
            
        Raises:
            Exception: If the function call fails
        """
        pass
    
    @abstractmethod
    def call_development_function_sync(self, func: Union[Callable[..., T], Callable[..., Awaitable[T]]], *args, **kwargs) -> T:
        """Synchronous version of call_development_function
        
        Args:
            func: The function to call
            *args: Positional arguments for the function
            **kwargs: Keyword arguments for the function
            
        Returns:
            The result of the function call
            
        Raises:
            Exception: If the function call fails
        """
        pass
    
    @abstractmethod
    async def handle_rfc(self, rfc_call: Dict[str, Any]) -> Any:
        """Handle incoming RFC calls
        
        Args:
            rfc_call: The RFC call data
            
        Returns:
            The result of handling the RFC call
        """
        pass
    
    @abstractmethod
    def is_connected(self) -> bool:
        """Check if the IPC connection is active
        
        Returns:
            True if connected, False otherwise
        """
        pass
    
    @abstractmethod
    def get_mode_name(self) -> str:
        """Get the name of the current IPC mode for logging
        
        Returns:
            A string describing the IPC mode
        """
        pass
    
    @abstractmethod
    def cleanup(self) -> None:
        """Clean up resources used by the IPC implementation"""
        pass
    
    @abstractmethod
    def get_health_status(self) -> Dict[str, Any]:
        """Get health status information
        
        Returns:
            Dictionary containing health status information
        """
        pass