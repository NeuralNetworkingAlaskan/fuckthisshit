import argparse
import inspect
import secrets
import logging
from typing import TypeVar, Callable, Awaitable, Union, overload, cast
from python.helpers import dotenv, rfc, settings
import asyncio
import threading
import queue

# Import new IPC components
from .ipc_factory import IPCFactory
from .feature_flags import FeatureFlags

T = TypeVar('T')
R = TypeVar('R')

# Initialize logging for runtime module
logger = logging.getLogger(__name__)

parser = argparse.ArgumentParser()
args = {}
dockerman = None
runtime_id = None


def initialize():
    global args
    if args:
        return
    parser.add_argument("--port", type=int, default=None, help="Web UI port")
    parser.add_argument("--host", type=str, default=None, help="Web UI host")
    parser.add_argument(
        "--cloudflare_tunnel",
        type=bool,
        default=False,
        help="Use cloudflare tunnel for public URL",
    )
    parser.add_argument(
        "--development", type=bool, default=False, help="Development mode"
    )

    known, unknown = parser.parse_known_args()
    args = vars(known)
    for arg in unknown:
        if "=" in arg:
            key, value = arg.split("=", 1)
            key = key.lstrip("-")
            args[key] = value

def get_arg(name: str):
    global args
    return args.get(name, None)

def has_arg(name: str):
    global args
    return name in args

def is_dockerized() -> bool:
    return bool(get_arg("dockerized"))

def is_development() -> bool:
    return not is_dockerized()

def get_local_url():
    if is_dockerized():
        return "host.docker.internal"
    return "127.0.0.1"

def get_runtime_id() -> str:
    global runtime_id
    if not runtime_id:
        runtime_id = secrets.token_hex(8)   
    return runtime_id

@overload
async def call_development_function(func: Callable[..., Awaitable[T]], *args, **kwargs) -> T: ...

@overload
async def call_development_function(func: Callable[..., T], *args, **kwargs) -> T: ...

async def call_development_function(func: Union[Callable[..., T], Callable[..., Awaitable[T]]], *args, **kwargs) -> T:
    """Call development function through IPC abstraction"""
    if is_development():
        # Use IPC abstraction instead of direct RFC calls
        try:
            ipc = IPCFactory.get_ipc()
            
            if FeatureFlags.is_debug_mode():
                logger.debug(f"Using IPC mode: {ipc.get_mode_name()} for {func.__module__}.{func.__name__}")
            
            return await ipc.call_development_function(func, *args, **kwargs)
            
        except Exception as e:
            logger.error(f"IPC call failed for {func.__module__}.{func.__name__}: {e}")
            
            # Enhanced error handling with fallback options
            if FeatureFlags.should_fallback_to_local():
                logger.warning(f"Attempting local execution fallback for {func.__name__}")
                try:
                    if inspect.iscoroutinefunction(func):
                        result = await func(*args, **kwargs)
                    else:
                        result = func(*args, **kwargs)
                    
                    logger.info(f"Local execution successful for {func.__name__}")
                    return cast(T, result)
                    
                except Exception as local_error:
                    logger.error(f"Local execution also failed for {func.__name__}: {local_error}")
                    # Re-raise the original IPC error
                    raise e
            
            raise
    else:
        # Direct execution in Docker mode
        if inspect.iscoroutinefunction(func):
            return await func(*args, **kwargs)
        else:
            return func(*args, **kwargs) # type: ignore


async def handle_rfc(rfc_call: rfc.RFCCall):
    """Handle RFC through IPC abstraction"""
    try:
        ipc = IPCFactory.get_ipc()
        # Convert RFCCall to dict for IPC interface
        rfc_dict = cast(dict, rfc_call)
        return await ipc.handle_rfc(rfc_dict)
    except Exception as e:
        logger.error(f"RFC handling failed: {e}")
        # Fallback to direct RFC handling
        return await rfc.handle_rfc(rfc_call=rfc_call, password=_get_rfc_password())


def call_development_function_sync(func: Union[Callable[..., T], Callable[..., Awaitable[T]]], *args, **kwargs) -> T:
    """Synchronous version using IPC abstraction"""
    if is_development():
        try:
            ipc = IPCFactory.get_ipc()
            
            if FeatureFlags.is_debug_mode():
                logger.debug(f"Using IPC mode (sync): {ipc.get_mode_name()} for {func.__module__}.{func.__name__}")
            
            return ipc.call_development_function_sync(func, *args, **kwargs)
            
        except Exception as e:
            logger.error(f"Sync IPC call failed for {func.__module__}.{func.__name__}: {e}")
            
            # Enhanced error handling with fallback options
            if FeatureFlags.should_fallback_to_local():
                logger.warning(f"Attempting local execution fallback for {func.__name__}")
                try:
                    if inspect.iscoroutinefunction(func):
                        result = asyncio.run(func(*args, **kwargs))
                    else:
                        result = func(*args, **kwargs)
                    
                    logger.info(f"Local execution successful for {func.__name__}")
                    return cast(T, result)
                    
                except Exception as local_error:
                    logger.error(f"Local execution also failed for {func.__name__}: {local_error}")
                    # Re-raise the original IPC error
                    raise e
            
            raise
    else:
        # Direct execution in Docker mode
        if inspect.iscoroutinefunction(func):
            return cast(T, asyncio.run(func(*args, **kwargs)))
        else:
            return cast(T, func(*args, **kwargs))


def _get_rfc_password() -> str:
    """Legacy function for backward compatibility"""
    password = dotenv.get_dotenv_value(dotenv.KEY_RFC_PASSWORD)
    if not password:
        raise Exception("No RFC password, cannot handle RFC calls.")
    return password


def _get_rfc_url() -> str:
    """Legacy function for backward compatibility"""
    set = settings.get_settings()
    url = set["rfc_url"]
    if not "://" in url:
        url = "http://"+url
    if url.endswith("/"):
        url = url[:-1]
    url = url+":"+str(set["rfc_port_http"])
    url += "/rfc"
    return url


# New utility functions for IPC management
def get_ipc_health_status() -> dict:
    """Get comprehensive IPC health status"""
    try:
        return IPCFactory.get_health_status()
    except Exception as e:
        logger.error(f"Failed to get IPC health status: {e}")
        return {
            'status': 'error',
            'error': str(e),
            'mode': 'unknown'
        }


def reset_ipc_connection():
    """Reset IPC connection (useful for configuration changes)"""
    try:
        IPCFactory.reset_ipc()
        logger.info("IPC connection reset successfully")
    except Exception as e:
        logger.error(f"Failed to reset IPC connection: {e}")
        raise


def is_ipc_available() -> bool:
    """Check if IPC is available and functional"""
    try:
        return IPCFactory.is_ipc_available()
    except Exception as e:
        logger.error(f"IPC availability check failed: {e}")
        return False


def get_web_ui_port():
    web_ui_port = (
        get_arg("port")
        or int(dotenv.get_dotenv_value("WEB_UI_PORT", 0))
        or 5000
    )
    return web_ui_port

def get_tunnel_api_port():
    tunnel_api_port = (
        get_arg("tunnel_api_port")
        or int(dotenv.get_dotenv_value("TUNNEL_API_PORT", 0))
        or 55520
    )
    return tunnel_api_port