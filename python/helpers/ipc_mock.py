import logging
import inspect
import asyncio
import os
from typing import Any, Dict, Optional, Callable, Union, TypeVar, Awaitable, cast
from .ipc_interface import AbstractAgentZeroIPC
from .feature_flags import FeatureFlags

logger = logging.getLogger(__name__)
T = TypeVar('T')

class MockAgentZeroIPC(AbstractAgentZeroIPC):
    """Mock IPC implementation for native mode operation"""
    
    def __init__(self):
        self.server_running = False
        self.call_count = 0
        self.error_count = 0
        logger.info("Initialized Mock IPC - Native mode active")
        logger.warning("RFC functionality will be mocked - limited functionality expected")
    
    async def call_development_function(self, func: Union[Callable[..., T], Callable[..., Awaitable[T]]], *args, **kwargs) -> T:
        """Execute function locally in native mode"""
        self.call_count += 1
        func_name = f"{func.__module__}.{func.__name__}" if hasattr(func, '__module__') else str(func)
        
        if FeatureFlags.is_debug_mode():
            logger.debug(f"MOCK IPC: Executing {func_name} locally with args={args}, kwargs={kwargs}")
        else:
            logger.debug(f"MOCK IPC: Executing {func_name} locally")
        
        try:
            if inspect.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                result = func(*args, **kwargs)
            
            if FeatureFlags.is_debug_mode():
                logger.debug(f"MOCK IPC: {func_name} completed successfully")
            
            return cast(T, result)
            
        except Exception as e:
            self.error_count += 1
            logger.error(f"Mock IPC function execution failed for {func_name}: {e}")
            
            # Check if we should fallback to mock responses
            if FeatureFlags.should_fallback_to_local() and hasattr(func, '__name__'):
                mock_response = self._get_mock_response(func.__name__, e)
                logger.warning(f"Returning mock response for {func.__name__}: {mock_response}")
                return mock_response
            
            raise
    
    def call_development_function_sync(self, func: Union[Callable[..., T], Callable[..., Awaitable[T]]], *args, **kwargs) -> T:
        """Synchronous version - execute locally"""
        self.call_count += 1
        func_name = f"{func.__module__}.{func.__name__}" if hasattr(func, '__module__') else str(func)
        
        if FeatureFlags.is_debug_mode():
            logger.debug(f"MOCK IPC SYNC: Executing {func_name} locally with args={args}, kwargs={kwargs}")
        else:
            logger.debug(f"MOCK IPC SYNC: Executing {func_name} locally")
        
        try:
            if inspect.iscoroutinefunction(func):
                # Run async function in sync context
                result = asyncio.run(func(*args, **kwargs))
            else:
                result = func(*args, **kwargs)
            
            if FeatureFlags.is_debug_mode():
                logger.debug(f"MOCK IPC SYNC: {func_name} completed successfully")
            
            return cast(T, result)
            
        except Exception as e:
            self.error_count += 1
            logger.error(f"Mock IPC sync function execution failed for {func_name}: {e}")
            
            # Check if we should fallback to mock responses
            if FeatureFlags.should_fallback_to_local() and hasattr(func, '__name__'):
                mock_response = self._get_mock_response(func.__name__, e)
                logger.warning(f"Returning mock response for {func.__name__}: {mock_response}")
                return mock_response
            
            raise
    
    def _get_mock_response(self, func_name: str, error: Exception) -> Any:
        """Generate appropriate mock responses for failed operations"""
        logger.debug(f"Generating mock response for {func_name}")
        
        # File existence checks
        if any(check in func_name.lower() for check in ['file_exists', 'path_exists', 'folder_exists']):
            return False
        
        # File reading operations
        elif any(read_op in func_name.lower() for read_op in ['read_file', 'get_file']):
            if 'base64' in func_name.lower():
                return ""  # Empty base64 string
            elif 'binary' in func_name.lower():
                return b""  # Empty bytes
            else:
                return ""  # Empty string
        
        # Directory listing operations
        elif any(list_op in func_name.lower() for list_op in ['list_folder', 'list_directory', 'get_subdirectories', 'get_files']):
            return []
        
        # File writing/modification operations
        elif any(write_op in func_name.lower() for write_op in ['write_file', 'delete_file', 'delete_folder', 'make_dirs', 'move_file', 'upload_file']):
            return True
        
        # Search operations
        elif 'search' in func_name.lower():
            return []
        
        # Generic operations that should return success
        elif any(op in func_name.lower() for op in ['create', 'update', 'save', 'set']):
            return True
        
        # Default mock response for unknown operations
        else:
            return {
                'status': 'mock_response',
                'message': f'Mock response for {func_name}',
                'error': str(error),
                'mock': True,
                'native_mode': True
            }
    
    async def handle_rfc(self, rfc_call: Dict[str, Any]) -> Any:
        """Mock RFC handler"""
        logger.info(f"MOCK: Handling RFC call (mock mode)")
        return {
            'status': 'mock_handled', 
            'mock': True,
            'message': 'RFC call handled in mock mode'
        }
    
    def is_connected(self) -> bool:
        """Always return True for mock mode"""
        return True
    
    def get_mode_name(self) -> str:
        """Return mode name for logging"""
        return "Mock (Native)"
    
    def cleanup(self) -> None:
        """Clean up mock resources"""
        logger.info("Mock IPC cleanup completed")
        self.server_running = False
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get health status information"""
        return {
            'mode': 'mock',
            'connected': True,
            'native_mode': True,
            'call_count': self.call_count,
            'error_count': self.error_count,
            'error_rate': self.error_count / max(self.call_count, 1),
            'features': {
                'debug_mode': FeatureFlags.is_debug_mode(),
                'fallback_enabled': FeatureFlags.should_fallback_to_local(),
                'timeout': FeatureFlags.get_ipc_timeout()
            }
        }