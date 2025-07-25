"""
Agent Zero gRPC IPC Implementation
Provides gRPC-based inter-process communication for native mode
"""

import asyncio
import logging
import time
import json
import inspect
import os
from typing import Any, Dict, Optional, Callable, Union, TypeVar, Awaitable, cast, List

import grpc
from python.helpers.grpc_proto import agent_zero_pb2, agent_zero_pb2_grpc
from .ipc_interface import AbstractAgentZeroIPC
from .feature_flags import FeatureFlags

logger = logging.getLogger(__name__)
T = TypeVar('T')

class GRPCAgentZeroIPC(AbstractAgentZeroIPC):
    """gRPC-based IPC implementation for Agent Zero"""
    
    def __init__(self, host: str = "localhost", port: int = 50051):
        self.host = host
        self.port = port
        self.channel = None
        self.stub = None
        self.call_count = 0
        self.error_count = 0
        self.connection_attempts = 0
        self.last_connection_attempt = 0
        
        logger.info(f"Initialized gRPC IPC client for {host}:{port}")
        self._ensure_connection()
    
    def _ensure_connection(self):
        """Ensure gRPC connection is established"""
        current_time = time.time()
        
        # Rate limit connection attempts (max 1 per second)
        if current_time - self.last_connection_attempt < 1.0:
            return
        
        self.last_connection_attempt = current_time
        self.connection_attempts += 1
        
        try:
            if self.channel is None:
                self.channel = grpc.aio.insecure_channel(f"{self.host}:{self.port}")
                self.stub = agent_zero_pb2_grpc.AgentZeroServiceStub(self.channel)
                logger.info(f"Established gRPC connection to {self.host}:{self.port}")
        except Exception as e:
            logger.error(f"Failed to establish gRPC connection (attempt {self.connection_attempts}): {e}")
            self.channel = None
            self.stub = None
    
    def _serialize_argument(self, value: Any) -> agent_zero_pb2.FunctionArgument:
        """Serialize Python value to FunctionArgument"""
        arg = agent_zero_pb2.FunctionArgument()
        
        if isinstance(value, str):
            arg.string_value = value
        elif isinstance(value, int):
            arg.int_value = value
        elif isinstance(value, float):
            arg.float_value = value
        elif isinstance(value, bool):
            arg.bool_value = value
        elif isinstance(value, bytes):
            arg.bytes_value = value
        else:
            # Serialize complex objects as JSON
            try:
                arg.json_value = json.dumps(value, default=str)
            except Exception as e:
                logger.warning(f"Failed to serialize argument {type(value)}: {e}")
                arg.string_value = str(value)
        
        return arg
    
    def _deserialize_argument(self, arg: agent_zero_pb2.FunctionArgument) -> Any:
        """Deserialize FunctionArgument to Python value"""
        if arg.HasField('string_value'):
            return arg.string_value
        elif arg.HasField('int_value'):
            return arg.int_value
        elif arg.HasField('float_value'):
            return arg.float_value
        elif arg.HasField('bool_value'):
            return arg.bool_value
        elif arg.HasField('bytes_value'):
            return arg.bytes_value
        elif arg.HasField('json_value'):
            try:
                return json.loads(arg.json_value)
            except Exception as e:
                logger.warning(f"Failed to deserialize JSON argument: {e}")
                return arg.json_value
        else:
            return None
    
    async def call_development_function(self, func: Union[Callable[..., T], Callable[..., Awaitable[T]]], *args, **kwargs) -> T:
        """Call a development function via gRPC"""
        self.call_count += 1
        func_name = func.__name__ if hasattr(func, '__name__') else str(func)
        module_name = func.__module__ if hasattr(func, '__module__') else "unknown"
        
        if FeatureFlags.is_debug_mode():
            logger.debug(f"gRPC IPC: Calling {module_name}.{func_name} with args={args}, kwargs={kwargs}")
        else:
            logger.debug(f"gRPC IPC: Calling {module_name}.{func_name}")
        
        try:
            self._ensure_connection()
            
            if self.stub is None:
                raise Exception("gRPC connection not available")
            
            # Prepare request
            request = agent_zero_pb2.FunctionRequest(
                function_name=func_name,
                module_name=module_name,
                args=[self._serialize_argument(arg) for arg in args],
                kwargs={key: self._serialize_argument(value) for key, value in kwargs.items()},
                is_async=inspect.iscoroutinefunction(func),
                timeout_seconds=FeatureFlags.get_ipc_timeout(),
                execution_id=f"grpc_{int(time.time() * 1000)}"
            )
            
            # Make gRPC call
            response = await self.stub.ExecuteFunction(request)
            
            if response.success:
                result = self._deserialize_argument(response.result)
                if FeatureFlags.is_debug_mode():
                    logger.debug(f"gRPC IPC: {func_name} completed successfully in {response.execution_time:.3f}s")
                return cast(T, result)
            else:
                self.error_count += 1
                logger.error(f"gRPC function execution failed for {func_name}: {response.error_message}")
                raise Exception(f"{response.error_type}: {response.error_message}")
                
        except Exception as e:
            self.error_count += 1
            logger.error(f"gRPC IPC call failed for {func_name}: {e}")
            
            # Check if we should fallback to local execution
            if FeatureFlags.should_fallback_to_local():
                logger.warning(f"Attempting local execution fallback for {func_name}")
                try:
                    if inspect.iscoroutinefunction(func):
                        result = await func(*args, **kwargs)
                    else:
                        result = func(*args, **kwargs)
                    
                    logger.info(f"Local execution successful for {func_name}")
                    return cast(T, result)
                    
                except Exception as local_error:
                    logger.error(f"Local execution also failed for {func_name}: {local_error}")
                    # Re-raise the original gRPC error
                    raise e
            
            raise
    
    def call_development_function_sync(self, func: Union[Callable[..., T], Callable[..., Awaitable[T]]], *args, **kwargs) -> T:
        """Synchronous version of call_development_function"""
        try:
            # Run the async version in a new event loop
            return asyncio.run(self.call_development_function(func, *args, **kwargs))
        except Exception as e:
            logger.error(f"Sync gRPC IPC call failed for {func.__name__}: {e}")
            
            # Check if we should fallback to local execution
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
                    # Re-raise the original gRPC error
                    raise e
            
            raise
    
    async def handle_rfc(self, rfc_call: Dict[str, Any]) -> Any:
        """Handle RFC calls via gRPC"""
        logger.info(f"gRPC IPC: Handling RFC call")
        
        try:
            self._ensure_connection()
            
            if self.stub is None:
                raise Exception("gRPC connection not available")
            
            # Convert RFC call to gRPC request
            request = agent_zero_pb2.RFCRequest(
                method=rfc_call.get('method', 'POST'),
                path=rfc_call.get('path', '/'),
                headers=rfc_call.get('headers', {}),
                body=rfc_call.get('body', b''),
                request_id=rfc_call.get('request_id', f"rfc_{int(time.time() * 1000)}")
            )
            
            response = await self.stub.HandleRFC(request)
            
            if response.success:
                return {
                    'status_code': response.status_code,
                    'headers': dict(response.headers),
                    'body': response.body,
                    'request_id': response.request_id
                }
            else:
                logger.error(f"gRPC RFC handling failed: {response.error_message}")
                return {
                    'status_code': response.status_code,
                    'error': response.error_message,
                    'request_id': response.request_id
                }
                
        except Exception as e:
            logger.error(f"gRPC RFC handling failed: {e}")
            return {
                'status_code': 500,
                'error': str(e),
                'grpc_error': True
            }
    
    def is_connected(self) -> bool:
        """Check if gRPC connection is active"""
        if self.channel is None or self.stub is None:
            return False
        
        try:
            # Try a simple ping to check connectivity
            request = agent_zero_pb2.PingRequest(
                message="connection_check",
                timestamp=int(time.time() * 1000)
            )
            
            # Use a short timeout for connection check
            future = self.stub.Ping(request, timeout=2.0)
            response = asyncio.run(asyncio.wait_for(future, timeout=2.0))
            return True
            
        except Exception as e:
            logger.debug(f"gRPC connection check failed: {e}")
            return False
    
    def get_mode_name(self) -> str:
        """Return mode name for logging"""
        return f"gRPC ({self.host}:{self.port})"
    
    def cleanup(self) -> None:
        """Clean up gRPC resources"""
        logger.info("Cleaning up gRPC IPC resources")
        
        if self.channel:
            try:
                asyncio.run(self.channel.close())
            except Exception as e:
                logger.warning(f"Error closing gRPC channel: {e}")
            finally:
                self.channel = None
                self.stub = None
        
        logger.info("gRPC IPC cleanup completed")
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get health status information"""
        try:
            # Try to get detailed health from server
            if self.stub:
                request = agent_zero_pb2.HealthRequest(detailed=True)
                response = asyncio.run(self.stub.GetHealth(request, timeout=5.0))
                
                return {
                    'mode': 'grpc',
                    'connected': response.healthy,
                    'server_status': response.status,
                    'server_uptime': response.uptime_seconds,
                    'server_memory': response.memory_usage,
                    'server_cpu': response.cpu_usage,
                    'server_details': dict(response.details),
                    'client_info': {
                        'host': self.host,
                        'port': self.port,
                        'call_count': self.call_count,
                        'error_count': self.error_count,
                        'error_rate': self.error_count / max(self.call_count, 1),
                        'connection_attempts': self.connection_attempts
                    },
                    'features': {
                        'debug_mode': FeatureFlags.is_debug_mode(),
                        'fallback_enabled': FeatureFlags.should_fallback_to_local(),
                        'timeout': FeatureFlags.get_ipc_timeout()
                    }
                }
            else:
                return {
                    'mode': 'grpc',
                    'connected': False,
                    'error': 'No gRPC connection',
                    'client_info': {
                        'host': self.host,
                        'port': self.port,
                        'call_count': self.call_count,
                        'error_count': self.error_count,
                        'connection_attempts': self.connection_attempts
                    }
                }
                
        except Exception as e:
            logger.error(f"Failed to get gRPC health status: {e}")
            return {
                'mode': 'grpc',
                'connected': False,
                'error': str(e),
                'client_info': {
                    'host': self.host,
                    'port': self.port,
                    'call_count': self.call_count,
                    'error_count': self.error_count,
                    'connection_attempts': self.connection_attempts
                }
            }
    
    # Additional gRPC-specific methods for file operations
    
    async def read_file(self, file_path: str, binary_mode: bool = False, encoding: str = 'utf-8', max_size: int = 0) -> Dict[str, Any]:
        """Read file via gRPC"""
        try:
            self._ensure_connection()
            
            if self.stub is None:
                raise Exception("gRPC connection not available")
            
            request = agent_zero_pb2.ReadFileRequest(
                file_path=file_path,
                binary_mode=binary_mode,
                encoding=encoding,
                max_size=max_size
            )
            
            response = await self.stub.ReadFile(request)
            
            if response.success:
                if response.HasField('text_content'):
                    return {
                        'success': True,
                        'content': response.text_content,
                        'size': response.file_size,
                        'encoding': response.file_encoding
                    }
                else:
                    return {
                        'success': True,
                        'content': response.binary_content,
                        'size': response.file_size,
                        'binary': True
                    }
            else:
                return {
                    'success': False,
                    'error': response.error_message
                }
                
        except Exception as e:
            logger.error(f"gRPC file read failed for {file_path}: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def write_file(self, file_path: str, content: Union[str, bytes], create_directories: bool = True, 
                        append_mode: bool = False, encoding: str = 'utf-8') -> Dict[str, Any]:
        """Write file via gRPC"""
        try:
            self._ensure_connection()
            
            if self.stub is None:
                raise Exception("gRPC connection not available")
            
            request = agent_zero_pb2.WriteFileRequest(
                file_path=file_path,
                create_directories=create_directories,
                append_mode=append_mode,
                encoding=encoding
            )
            
            if isinstance(content, str):
                request.text_content = content
            else:
                request.binary_content = content
            
            response = await self.stub.WriteFile(request)
            
            return {
                'success': response.success,
                'bytes_written': response.bytes_written if response.success else 0,
                'error': response.error_message if not response.success else None
            }
            
        except Exception as e:
            logger.error(f"gRPC file write failed for {file_path}: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def execute_command(self, command: str, args: Optional[List[str]] = None, working_directory: Optional[str] = None,
                             environment: Optional[Dict[str, str]] = None, timeout_seconds: int = 0,
                             capture_output: bool = True) -> Dict[str, Any]:
        """Execute command via gRPC"""
        try:
            self._ensure_connection()
            
            if self.stub is None:
                raise Exception("gRPC connection not available")
            
            request = agent_zero_pb2.CommandRequest(
                command=command,
                args=args or [],
                working_directory=working_directory or "",
                environment=environment or {},
                timeout_seconds=timeout_seconds,
                capture_output=capture_output,
                execution_id=f"cmd_{int(time.time() * 1000)}"
            )
            
            response = await self.stub.ExecuteCommand(request)
            
            return {
                'success': response.success,
                'exit_code': response.exit_code,
                'stdout': response.stdout,
                'stderr': response.stderr,
                'execution_time': response.execution_time,
                'execution_id': response.execution_id,
                'error': response.error_message if not response.success else None
            }
            
        except Exception as e:
            logger.error(f"gRPC command execution failed for {command}: {e}")
            return {
                'success': False,
                'exit_code': -1,
                'error': str(e)
            }


# Factory function for creating gRPC IPC instances
def create_grpc_ipc(host: Optional[str] = None, port: Optional[int] = None) -> GRPCAgentZeroIPC:
    """Create a gRPC IPC instance with configuration from environment"""
    host = host or os.environ.get('AGENT_ZERO_GRPC_HOST', 'localhost')
    port = port or int(os.environ.get('AGENT_ZERO_GRPC_PORT', '50051'))
    
    return GRPCAgentZeroIPC(host, port)