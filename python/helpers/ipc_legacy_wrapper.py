import logging
import inspect
import asyncio
import queue
import threading
from typing import Any, Dict, Optional, Callable, Union, TypeVar, Awaitable, cast
from .ipc_interface import AbstractAgentZeroIPC
from .feature_flags import FeatureFlags

logger = logging.getLogger(__name__)
T = TypeVar('T')

class LegacyRFCWrapper(AbstractAgentZeroIPC):
    """Wrapper around existing RFC implementation"""
    
    def __init__(self):
        self.call_count = 0
        self.error_count = 0
        self._rfc_available = None  # Cache RFC availability check
        logger.info("Initialized Legacy RFC wrapper")
    
    async def call_development_function(self, func: Union[Callable[..., T], Callable[..., Awaitable[T]]], *args, **kwargs) -> T:
        """Delegate to existing RFC implementation"""
        self.call_count += 1
        func_name = f"{func.__module__}.{func.__name__}" if hasattr(func, '__module__') else str(func)
        
        try:
            # Use existing RFC logic from runtime.py
            from . import rfc
            
            url = self._get_rfc_url()
            password = self._get_rfc_password()
            
            if FeatureFlags.is_debug_mode():
                logger.debug(f"LEGACY RFC: Calling {func_name} via RFC to {url}")
            
            result = await rfc.call_rfc(
                url=url,
                password=password,
                module=func.__module__,
                function_name=func.__name__,
                args=list(args),
                kwargs=kwargs,
            )
            
            if FeatureFlags.is_debug_mode():
                logger.debug(f"LEGACY RFC: {func_name} completed successfully")
            
            return cast(T, result)
            
        except Exception as e:
            self.error_count += 1
            logger.error(f"Legacy RFC call failed for {func_name}: {e}")
            
            # In native mode or if fallback is enabled, try local execution
            if FeatureFlags.is_native_mode() or FeatureFlags.should_fallback_to_local():
                logger.warning(f"RFC failed, attempting local execution for {func_name}")
                try:
                    if inspect.iscoroutinefunction(func):
                        result = await func(*args, **kwargs)
                    else:
                        result = func(*args, **kwargs)
                    
                    logger.info(f"Local execution successful for {func_name}")
                    return cast(T, result)
                    
                except Exception as local_error:
                    logger.error(f"Local execution also failed for {func_name}: {local_error}")
                    # Re-raise the original RFC error
                    raise e
            
            raise
    
    def call_development_function_sync(self, func: Union[Callable[..., T], Callable[..., Awaitable[T]]], *args, **kwargs) -> T:
        """Synchronous version using existing runtime logic"""
        self.call_count += 1
        func_name = f"{func.__module__}.{func.__name__}" if hasattr(func, '__module__') else str(func)
        
        result_queue: queue.Queue = queue.Queue()
        
        def run_in_thread():
            try:
                result = asyncio.run(self.call_development_function(func, *args, **kwargs))
                result_queue.put(('success', result))
            except Exception as e:
                result_queue.put(('error', e))
        
        thread = threading.Thread(target=run_in_thread)
        thread.start()
        
        timeout = FeatureFlags.get_ipc_timeout()
        thread.join(timeout=timeout)
        
        if thread.is_alive():
            error_msg = f"RFC call timed out after {timeout} seconds for {func_name}"
            logger.error(error_msg)
            
            # Try local execution as fallback for timeout
            if FeatureFlags.should_fallback_to_local():
                logger.warning(f"Timeout occurred, attempting local execution for {func_name}")
                try:
                    if inspect.iscoroutinefunction(func):
                        result = asyncio.run(func(*args, **kwargs))
                    else:
                        result = func(*args, **kwargs)
                    
                    logger.info(f"Local execution successful after timeout for {func_name}")
                    return cast(T, result)
                    
                except Exception as local_error:
                    logger.error(f"Local execution failed after timeout for {func_name}: {local_error}")
            
            raise TimeoutError(error_msg)
        
        try:
            status, result = result_queue.get_nowait()
            if status == 'error':
                raise result
            return cast(T, result)
        except queue.Empty:
            raise RuntimeError(f"No result received for {func_name}")
    
    async def handle_rfc(self, rfc_call: Dict[str, Any]) -> Any:
        """Delegate to existing RFC handler"""
        try:
            from . import runtime, rfc
            # Convert dict to proper RFCCall type
            if isinstance(rfc_call, dict) and 'rfc_input' in rfc_call and 'hash' in rfc_call:
                # Already in correct format, cast to RFCCall
                typed_rfc_call = cast(rfc.RFCCall, rfc_call)
                return await runtime.handle_rfc(typed_rfc_call)
            else:
                # Try to cast as RFCCall anyway
                typed_rfc_call = cast(rfc.RFCCall, rfc_call)
                return await rfc.handle_rfc(typed_rfc_call, self._get_rfc_password())
        except Exception as e:
            logger.error(f"Legacy RFC handler failed: {e}")
            return {
                'status': 'error',
                'message': 'RFC handler failed',
                'error': str(e)
            }
    
    def is_connected(self) -> bool:
        """Check RFC connection by attempting to get configuration"""
        if self._rfc_available is not None:
            return self._rfc_available
        
        try:
            # Try to get RFC configuration
            url = self._get_rfc_url()
            password = self._get_rfc_password()
            
            # Basic validation
            if url and password:
                self._rfc_available = True
                return True
            else:
                self._rfc_available = False
                return False
                
        except Exception as e:
            logger.debug(f"RFC connection check failed: {e}")
            self._rfc_available = False
            return False
    
    def get_mode_name(self) -> str:
        """Return mode name for logging"""
        return "Legacy RFC"
    
    def cleanup(self) -> None:
        """Clean up RFC resources"""
        logger.info("Legacy RFC cleanup completed")
        self._rfc_available = None
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get health status information"""
        connected = self.is_connected()
        
        return {
            'mode': 'legacy_rfc',
            'connected': connected,
            'native_mode': False,
            'call_count': self.call_count,
            'error_count': self.error_count,
            'error_rate': self.error_count / max(self.call_count, 1),
            'rfc_config': {
                'host': FeatureFlags.get_rfc_host(),
                'port': FeatureFlags.get_rfc_port(),
                'timeout': FeatureFlags.get_ipc_timeout()
            },
            'features': {
                'debug_mode': FeatureFlags.is_debug_mode(),
                'fallback_enabled': FeatureFlags.should_fallback_to_local()
            }
        }
    
    def _get_rfc_password(self) -> str:
        """Get RFC password from existing dotenv logic"""
        try:
            from . import dotenv
            password = dotenv.get_dotenv_value(dotenv.KEY_RFC_PASSWORD)
            if not password:
                raise Exception("No RFC password configured")
            return password
        except ImportError:
            raise Exception("Cannot import dotenv module")
    
    def _get_rfc_url(self) -> str:
        """Get RFC URL from existing settings logic"""
        try:
            from . import settings
            set_config = settings.get_settings()
            url = set_config["rfc_url"]
            
            if not "://" in url:
                url = "http://" + url
            if url.endswith("/"):
                url = url[:-1]
            
            url = url + ":" + str(set_config["rfc_port_http"])
            url += "/rfc"
            
            return url
        except ImportError:
            # Fallback to environment variables
            host = FeatureFlags.get_rfc_host()
            port = FeatureFlags.get_rfc_port()
            return f"http://{host}:{port}/rfc"
        except Exception as e:
            logger.error(f"Failed to get RFC URL from settings: {e}")
            # Fallback to environment variables
            host = FeatureFlags.get_rfc_host()
            port = FeatureFlags.get_rfc_port()
            return f"http://{host}:{port}/rfc"