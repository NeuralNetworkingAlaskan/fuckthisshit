"""
Agent Zero gRPC Server Implementation
Provides native mode operations through gRPC interface
"""

import asyncio
import logging
import os
import shutil
import subprocess
import time
import json
import inspect
import importlib
import sys
from concurrent import futures
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, Callable
import threading
import psutil

import grpc
from python.helpers.grpc_proto import agent_zero_pb2, agent_zero_pb2_grpc
from .feature_flags import FeatureFlags

logger = logging.getLogger(__name__)

class AgentZeroGRPCServer(agent_zero_pb2_grpc.AgentZeroServiceServicer):
    """gRPC server implementation for Agent Zero native mode"""
    
    def __init__(self):
        self.start_time = time.time()
        self.request_count = 0
        self.success_count = 0
        self.error_count = 0
        self.total_execution_time = 0.0
        self._lock = threading.Lock()
        
        logger.info("Initialized Agent Zero gRPC Server")
    
    def _record_request(self, success: bool, execution_time: float):
        """Record request metrics"""
        with self._lock:
            self.request_count += 1
            self.total_execution_time += execution_time
            if success:
                self.success_count += 1
            else:
                self.error_count += 1
    
    def _serialize_argument(self, value: Any) -> agent_zero_pb2.FunctionArgument: # type: ignore
        """Serialize Python value to FunctionArgument"""
        arg = agent_zero_pb2.FunctionArgument() # type: ignore
        
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
    
    def _deserialize_argument(self, arg: agent_zero_pb2.FunctionArgument) -> Any: # type: ignore
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
    
    def _import_function(self, module_name: str, function_name: str) -> Optional[Callable]:
        """Import and return a function from a module"""
        try:
            module = importlib.import_module(module_name)
            return getattr(module, function_name)
        except Exception as e:
            logger.error(f"Failed to import {module_name}.{function_name}: {e}")
            return None
    
    async def ExecuteFunction(self, request, context):
        """Execute a function call"""
        start_time = time.time()
        execution_id = request.execution_id or f"exec_{int(time.time() * 1000)}"
        
        logger.debug(f"[{execution_id}] Executing function {request.module_name}.{request.function_name}")
        
        try:
            # Import the function
            func = self._import_function(request.module_name, request.function_name)
            if func is None:
                raise Exception(f"Function {request.module_name}.{request.function_name} not found")
            
            # Deserialize arguments
            args = [self._deserialize_argument(arg) for arg in request.args]
            kwargs = {key: self._deserialize_argument(value) for key, value in request.kwargs.items()}
            
            # Execute function
            if request.is_async and inspect.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            elif request.is_async and not inspect.iscoroutinefunction(func):
                # Run sync function in thread pool for async context
                loop = asyncio.get_event_loop()
                result = await loop.run_in_executor(None, func, *args, **kwargs)
            else:
                result = func(*args, **kwargs)
            
            execution_time = time.time() - start_time
            self._record_request(True, execution_time)
            
            logger.debug(f"[{execution_id}] Function executed successfully in {execution_time:.3f}s")
            
            return agent_zero_pb2.FunctionResponse( # type: ignore
                success=True,
                result=self._serialize_argument(result),
                execution_time=execution_time,
                execution_id=execution_id
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            self._record_request(False, execution_time)
            
            logger.error(f"[{execution_id}] Function execution failed: {e}")
            
            return agent_zero_pb2.FunctionResponse( # type: ignore
                success=False,
                error_message=str(e),
                error_type=type(e).__name__,
                traceback=str(e),  # Could be enhanced with full traceback
                execution_time=execution_time,
                execution_id=execution_id
            )
    
    async def HandleRFC(self, request, context):
        """Handle RFC calls"""
        logger.info(f"Handling RFC call: {request.method} {request.path}")
        
        try:
            # This is a placeholder - in a real implementation, you'd route this
            # to the appropriate handler based on the path and method
            response_body = json.dumps({
                "status": "handled",
                "method": request.method,
                "path": request.path,
                "message": "RFC handled by gRPC server"
            }).encode()
            
            return agent_zero_pb2.RFCResponse( # type: ignore
                status_code=200,
                body=response_body,
                request_id=request.request_id,
                success=True
            )
            
        except Exception as e:
            logger.error(f"RFC handling failed: {e}")
            return agent_zero_pb2.RFCResponse( # type: ignore
                status_code=500,
                request_id=request.request_id,
                success=False,
                error_message=str(e)
            )
    
    async def ReadFile(self, request, context):
        """Read file contents"""
        try:
            file_path = Path(request.file_path)
            
            if not file_path.exists():
                return agent_zero_pb2.ReadFileResponse( # type: ignore
                    success=False,
                    error_message=f"File not found: {request.file_path}"
                )
            
            if request.max_size > 0 and file_path.stat().st_size > request.max_size:
                return agent_zero_pb2.ReadFileResponse( # type: ignore
                    success=False,
                    error_message=f"File too large: {file_path.stat().st_size} > {request.max_size}"
                )
            
            if request.binary_mode:
                content = file_path.read_bytes()
                return agent_zero_pb2.ReadFileResponse( # type: ignore
                    success=True,
                    binary_content=content,
                    file_size=len(content)
                )
            else:
                encoding = request.encoding or 'utf-8'
                content = file_path.read_text(encoding=encoding)
                return agent_zero_pb2.ReadFileResponse( # type: ignore
                    success=True,
                    text_content=content,
                    file_size=len(content.encode(encoding)),
                    file_encoding=encoding
                )
                
        except Exception as e:
            logger.error(f"Failed to read file {request.file_path}: {e}")
            return agent_zero_pb2.ReadFileResponse( # type: ignore
                success=False,
                error_message=str(e)
            )
    
    async def WriteFile(self, request, context):
        """Write file contents"""
        try:
            file_path = Path(request.file_path)
            
            if request.create_directories:
                file_path.parent.mkdir(parents=True, exist_ok=True)
            
            if request.HasField('text_content'):
                encoding = request.encoding or 'utf-8'
                if request.append_mode:
                    with open(file_path, 'a', encoding=encoding) as f:
                        f.write(request.text_content)
                else:
                    file_path.write_text(request.text_content, encoding=encoding)
                bytes_written = len(request.text_content.encode(encoding))
            else:
                mode = 'ab' if request.append_mode else 'wb'
                with open(file_path, mode) as f:
                    f.write(request.binary_content)
                bytes_written = len(request.binary_content)
            
            return agent_zero_pb2.WriteFileResponse( # type: ignore
                success=True,
                bytes_written=bytes_written
            )
            
        except Exception as e:
            logger.error(f"Failed to write file {request.file_path}: {e}")
            return agent_zero_pb2.WriteFileResponse( # type: ignore
                success=False,
                error_message=str(e)
            )
    
    async def DeleteFile(self, request, context):
        """Delete file or directory"""
        try:
            file_path = Path(request.file_path)
            
            if not file_path.exists():
                return agent_zero_pb2.DeleteFileResponse( # type: ignore
                    success=False,
                    error_message=f"Path not found: {request.file_path}"
                )
            
            if file_path.is_file():
                file_path.unlink()
            elif file_path.is_dir():
                if request.recursive:
                    shutil.rmtree(file_path)
                else:
                    file_path.rmdir()
            
            return agent_zero_pb2.DeleteFileResponse(success=True) # type: ignore
            
        except Exception as e:
            logger.error(f"Failed to delete {request.file_path}: {e}")
            return agent_zero_pb2.DeleteFileResponse( # type: ignore
                success=False,
                error_message=str(e)
            )
    
    async def ListDirectory(self, request, context):
        """List directory contents"""
        try:
            dir_path = Path(request.directory_path)
            
            if not dir_path.exists() or not dir_path.is_dir():
                return agent_zero_pb2.ListDirectoryResponse( # type: ignore
                    success=False,
                    error_message=f"Directory not found: {request.directory_path}"
                )
            
            files = []
            
            if request.recursive:
                pattern = "**/*"
            else:
                pattern = "*"
            
            for path in dir_path.glob(pattern):
                if not request.include_hidden and path.name.startswith('.'):
                    continue
                
                # Apply file patterns if specified
                if request.file_patterns:
                    match_pattern = False
                    for pattern in request.file_patterns:
                        if path.match(pattern):
                            match_pattern = True
                            break
                    if not match_pattern:
                        continue
                
                try:
                    stat = path.stat()
                    file_info = agent_zero_pb2.FileInfo( # type: ignore
                        name=path.name,
                        path=str(path),
                        is_directory=path.is_dir(),
                        size=stat.st_size if path.is_file() else 0,
                        modified_time=int(stat.st_mtime),
                        permissions=oct(stat.st_mode)[-3:]
                    )
                    files.append(file_info)
                except Exception as e:
                    logger.warning(f"Failed to get info for {path}: {e}")
                    continue
            
            return agent_zero_pb2.ListDirectoryResponse( # type: ignore
                success=True,
                files=files
            )
            
        except Exception as e:
            logger.error(f"Failed to list directory {request.directory_path}: {e}")
            return agent_zero_pb2.ListDirectoryResponse( # type: ignore
                success=False,
                error_message=str(e)
            )
    
    async def FileExists(self, request, context):
        """Check if file exists"""
        try:
            file_path = Path(request.file_path)
            exists = file_path.exists()
            
            return agent_zero_pb2.FileExistsResponse( # type: ignore
                exists=exists,
                is_directory=file_path.is_dir() if exists else False,
                is_file=file_path.is_file() if exists else False
            )
            
        except Exception as e:
            logger.error(f"Failed to check file existence {request.file_path}: {e}")
            return agent_zero_pb2.FileExistsResponse(exists=False) # type: ignore
    
    async def CreateDirectory(self, request, context):
        """Create directory"""
        try:
            dir_path = Path(request.directory_path)
            dir_path.mkdir(parents=request.create_parents, exist_ok=True)
            
            return agent_zero_pb2.CreateDirectoryResponse(success=True) # type: ignore
            
        except Exception as e:
            logger.error(f"Failed to create directory {request.directory_path}: {e}")
            return agent_zero_pb2.CreateDirectoryResponse( # type: ignore
                success=False,
                error_message=str(e)
            )
    
    async def MoveFile(self, request, context):
        """Move/rename file"""
        try:
            source = Path(request.source_path)
            destination = Path(request.destination_path)
            
            if not source.exists():
                return agent_zero_pb2.MoveFileResponse( # type: ignore
                    success=False,
                    error_message=f"Source not found: {request.source_path}"
                )
            
            if destination.exists() and not request.overwrite:
                return agent_zero_pb2.MoveFileResponse( # type: ignore
                    success=False,
                    error_message=f"Destination exists: {request.destination_path}"
                )
            
            shutil.move(str(source), str(destination))
            
            return agent_zero_pb2.MoveFileResponse(success=True) # type: ignore
            
        except Exception as e:
            logger.error(f"Failed to move {request.source_path} to {request.destination_path}: {e}")
            return agent_zero_pb2.MoveFileResponse( # type: ignore
                success=False,
                error_message=str(e)
            )
    
    async def CopyFile(self, request, context):
        """Copy file or directory"""
        try:
            source = Path(request.source_path)
            destination = Path(request.destination_path)
            
            if not source.exists():
                return agent_zero_pb2.CopyFileResponse( # type: ignore
                    success=False,
                    error_message=f"Source not found: {request.source_path}"
                )
            
            if destination.exists() and not request.overwrite:
                return agent_zero_pb2.CopyFileResponse( # type: ignore
                    success=False,
                    error_message=f"Destination exists: {request.destination_path}"
                )
            
            if source.is_file():
                shutil.copy2(str(source), str(destination))
            elif source.is_dir() and request.recursive:
                shutil.copytree(str(source), str(destination), dirs_exist_ok=request.overwrite)
            else:
                return agent_zero_pb2.CopyFileResponse( # type: ignore
                    success=False,
                    error_message="Cannot copy directory without recursive flag"
                )
            
            return agent_zero_pb2.CopyFileResponse(success=True) # type: ignore
            
        except Exception as e:
            logger.error(f"Failed to copy {request.source_path} to {request.destination_path}: {e}")
            return agent_zero_pb2.CopyFileResponse( # type: ignore
                success=False,
                error_message=str(e)
            )
    
    async def ExecuteCommand(self, request, context):
        """Execute system command"""
        start_time = time.time()
        execution_id = request.execution_id or f"cmd_{int(time.time() * 1000)}"
        
        logger.debug(f"[{execution_id}] Executing command: {request.command}")
        
        try:
            # Prepare command
            if request.args:
                cmd = [request.command] + list(request.args)
            else:
                cmd = request.command
            
            # Prepare environment
            env = dict(os.environ)
            if request.environment:
                env.update(request.environment)
            
            # Execute command
            result = subprocess.run(
                cmd,
                cwd=request.working_directory or None,
                env=env,
                capture_output=request.capture_output,
                text=True,
                timeout=request.timeout_seconds if request.timeout_seconds > 0 else None
            )
            
            execution_time = time.time() - start_time
            
            logger.debug(f"[{execution_id}] Command completed with exit code {result.returncode} in {execution_time:.3f}s")
            
            return agent_zero_pb2.CommandResponse( # type: ignore
                success=result.returncode == 0,
                exit_code=result.returncode,
                stdout=result.stdout or "",
                stderr=result.stderr or "",
                execution_time=execution_time,
                execution_id=execution_id
            )
            
        except subprocess.TimeoutExpired as e:
            execution_time = time.time() - start_time
            logger.error(f"[{execution_id}] Command timed out after {execution_time:.3f}s")
            
            return agent_zero_pb2.CommandResponse( # type: ignore
                success=False,
                exit_code=-1,
                error_message=f"Command timed out after {request.timeout_seconds}s",
                execution_time=execution_time,
                execution_id=execution_id
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"[{execution_id}] Command execution failed: {e}")
            
            return agent_zero_pb2.CommandResponse( # type: ignore
                success=False,
                exit_code=-1,
                error_message=str(e),
                execution_time=execution_time,
                execution_id=execution_id
            )
    
    async def GetHealth(self, request, context):
        """Get server health status"""
        try:
            uptime = time.time() - self.start_time
            
            # Get system metrics if detailed info requested
            memory_usage = 0
            cpu_usage = 0.0
            
            if request.detailed:
                try:
                    process = psutil.Process()
                    memory_usage = process.memory_info().rss
                    cpu_usage = process.cpu_percent()
                except Exception as e:
                    logger.warning(f"Failed to get system metrics: {e}")
            
            details = {
                "mode": "grpc",
                "requests_total": str(self.request_count),
                "requests_successful": str(self.success_count),
                "requests_failed": str(self.error_count),
                "average_response_time": str(self.total_execution_time / max(self.request_count, 1))
            }
            
            return agent_zero_pb2.HealthResponse( # type: ignore
                healthy=True,
                status="healthy",
                details=details,
                uptime_seconds=uptime,
                memory_usage=memory_usage,
                cpu_usage=cpu_usage
            )
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return agent_zero_pb2.HealthResponse( # type: ignore
                healthy=False,
                status="error",
                details={"error": str(e)}
            )
    
    async def GetStatus(self, request, context):
        """Get server status"""
        try:
            avg_response_time = self.total_execution_time / max(self.request_count, 1)
            
            config = {
                "native_mode": str(FeatureFlags.is_native_mode()),
                "debug_mode": str(FeatureFlags.is_debug_mode()),
                "grpc_enabled": "true",
                "timeout": str(FeatureFlags.get_ipc_timeout())
            }
            
            return agent_zero_pb2.StatusResponse( # type: ignore
                mode="grpc",
                connected=True,
                total_requests=self.request_count,
                successful_requests=self.success_count,
                failed_requests=self.error_count,
                average_response_time=avg_response_time,
                configuration=config
            )
            
        except Exception as e:
            logger.error(f"Status check failed: {e}")
            return agent_zero_pb2.StatusResponse( # type: ignore
                mode="grpc",
                connected=False
            )
    
    async def Ping(self, request, context):
        """Ping server"""
        response_time = int(time.time() * 1000)
        latency = response_time - request.timestamp if request.timestamp > 0 else 0
        
        return agent_zero_pb2.PingResponse( # type: ignore
            message=f"Pong: {request.message}",
            request_timestamp=request.timestamp,
            response_timestamp=response_time,
            latency_ms=latency
        )


class GRPCServerManager:
    """Manager for the gRPC server lifecycle"""
    
    def __init__(self, host: str = "localhost", port: int = 50051):
        self.host = host
        self.port = port
        self.server = None
        self.servicer = None
        
    async def start_server(self):
        """Start the gRPC server"""
        self.server = grpc.aio.server(futures.ThreadPoolExecutor(max_workers=10))
        self.servicer = AgentZeroGRPCServer()
        
        agent_zero_pb2_grpc.add_AgentZeroServiceServicer_to_server(self.servicer, self.server)
        
        listen_addr = f"{self.host}:{self.port}"
        cert = FeatureFlags.get_grpc_cert()
        key = FeatureFlags.get_grpc_key()

        if cert and key:
            with open(cert, 'rb') as f:
                certificate_chain = f.read()
            with open(key, 'rb') as f:
                private_key = f.read()
            root_cert = FeatureFlags.get_grpc_root_cert()
            root_bytes = None
            if root_cert:
                with open(root_cert, 'rb') as f:
                    root_bytes = f.read()
            server_credentials = grpc.ssl_server_credentials(
                [(private_key, certificate_chain)],
                root_certificates=root_bytes,
                require_client_auth=bool(root_bytes),
            )
            self.server.add_secure_port(listen_addr, server_credentials)
            logger.info(f"Starting secure Agent Zero gRPC server on {listen_addr}")
        else:
            self.server.add_insecure_port(listen_addr)
            logger.info(f"Starting Agent Zero gRPC server on {listen_addr}")
        await self.server.start()
        
        logger.info("Agent Zero gRPC server started successfully")
        return self.server
    
    async def stop_server(self):
        """Stop the gRPC server"""
        if self.server:
            logger.info("Stopping Agent Zero gRPC server")
            await self.server.stop(grace=5)
            logger.info("Agent Zero gRPC server stopped")
    
    async def wait_for_termination(self):
        """Wait for server termination"""
        if self.server:
            await self.server.wait_for_termination()


# Standalone server runner
async def run_grpc_server():
    """Run the gRPC server as a standalone service"""
    host = os.environ.get('AGENT_ZERO_GRPC_HOST', 'localhost')
    port = int(os.environ.get('AGENT_ZERO_GRPC_PORT', '50051'))
    
    manager = GRPCServerManager(host, port)
    
    try:
        await manager.start_server()
        await manager.wait_for_termination()
    except KeyboardInterrupt:
        logger.info("Received interrupt signal")
    finally:
        await manager.stop_server()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(run_grpc_server())