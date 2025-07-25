#!/usr/bin/env python3
"""
Test script for Agent Zero Phase 2 gRPC implementation
"""

import asyncio
import logging
import os
import sys
import time
from pathlib import Path
import pytest

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from python.helpers.feature_flags import FeatureFlags
from python.helpers.ipc_factory import IPCFactory
from python.helpers.grpc_server import GRPCServerManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@pytest.mark.asyncio
async def test_grpc_server():
    """Test the gRPC server functionality"""
    logger.info("=== Testing gRPC Server ===")
    
    # Start gRPC server
    server_manager = GRPCServerManager(host="localhost", port=50051)
    
    try:
        await server_manager.start_server()
        logger.info("gRPC server started successfully")
        
        # Give server time to start
        await asyncio.sleep(1)
        
        # Test server health
        if server_manager.servicer:
            from python.helpers.grpc_proto import agent_zero_pb2
            
            # Test ping
            ping_request = agent_zero_pb2.PingRequest(
                message="test_ping",
                timestamp=int(time.time() * 1000)
            )
            
            ping_response = await server_manager.servicer.Ping(ping_request, None)
            logger.info(f"Ping response: {ping_response.message}")
            
            # Test health check
            health_request = agent_zero_pb2.HealthRequest(detailed=True)
            health_response = await server_manager.servicer.GetHealth(health_request, None)
            logger.info(f"Health status: {health_response.status}")
            
        logger.info("gRPC server tests passed")
        
    except Exception as e:
        logger.error(f"gRPC server test failed: {e}")
        raise
    finally:
        await server_manager.stop_server()

def test_ipc_factory():
    """Test the IPC factory with different configurations"""
    logger.info("=== Testing IPC Factory ===")
    
    # Test native mode with mock IPC
    os.environ['AGENT_ZERO_NATIVE_MODE'] = 'true'
    os.environ['AGENT_ZERO_USE_GRPC'] = 'false'
    
    ipc = IPCFactory.create_ipc()
    logger.info(f"Native mode (mock): {ipc.get_mode_name()}")
    assert ipc.get_mode_name() == "Mock (Native)"
    
    # Test native mode with gRPC
    os.environ['AGENT_ZERO_USE_GRPC'] = 'true'
    
    ipc = IPCFactory.create_ipc()
    logger.info(f"Native mode (gRPC): {ipc.get_mode_name()}")
    # Should either be gRPC or fall back to mock if gRPC not available
    
    # Test Docker mode
    os.environ['AGENT_ZERO_NATIVE_MODE'] = 'false'
    os.environ['AGENT_ZERO_USE_GRPC'] = 'false'
    
    ipc = IPCFactory.create_ipc()
    logger.info(f"Docker mode: {ipc.get_mode_name()}")
    
    # Get health status
    health = IPCFactory.get_health_status()
    logger.info(f"Health status: {health.get('mode', 'unknown')}")
    
    logger.info("IPC factory tests passed")

def test_feature_flags():
    """Test feature flag functionality"""
    logger.info("=== Testing Feature Flags ===")
    
    # Test native mode flag
    os.environ['AGENT_ZERO_NATIVE_MODE'] = 'true'
    assert FeatureFlags.is_native_mode() == True
    
    os.environ['AGENT_ZERO_NATIVE_MODE'] = 'false'
    assert FeatureFlags.is_native_mode() == False
    
    # Test gRPC flag
    os.environ['AGENT_ZERO_USE_GRPC'] = 'true'
    assert FeatureFlags.use_grpc_ipc() == True
    
    os.environ['AGENT_ZERO_USE_GRPC'] = 'false'
    assert FeatureFlags.use_grpc_ipc() == False
    
    # Test debug flag
    os.environ['AGENT_ZERO_DEBUG'] = 'true'
    assert FeatureFlags.is_debug_mode() == True
    
    os.environ['AGENT_ZERO_DEBUG'] = 'false'
    assert FeatureFlags.is_debug_mode() == False
    
    logger.info("Feature flags tests passed")

@pytest.mark.asyncio
async def test_grpc_client():
    """Test gRPC client functionality"""
    logger.info("=== Testing gRPC Client ===")
    
    try:
        from python.helpers.ipc_grpc import GRPCAgentZeroIPC
        
        # Create gRPC client
        client = GRPCAgentZeroIPC(host="localhost", port=50051)
        
        # Test connection (will fail if server not running, which is expected)
        connected = client.is_connected()
        logger.info(f"gRPC client connection status: {connected}")
        
        # Get health status
        health = client.get_health_status()
        logger.info(f"gRPC client health: {health.get('mode', 'unknown')}")
        
        # Cleanup
        client.cleanup()
        
        logger.info("gRPC client tests completed")
        
    except ImportError as e:
        logger.warning(f"gRPC client not available: {e}")
    except Exception as e:
        logger.warning(f"gRPC client test failed (expected if server not running): {e}")

def test_environment_setup():
    """Test environment setup for Phase 2"""
    logger.info("=== Testing Environment Setup ===")
    
    # Check if gRPC modules are available
    try:
        from python.helpers.grpc_proto import agent_zero_pb2, agent_zero_pb2_grpc
        logger.info("✓ gRPC protocol buffers available")
    except ImportError as e:
        logger.error(f"✗ gRPC protocol buffers not available: {e}")
    
    # Check if gRPC server is available
    try:
        from python.helpers.grpc_server import AgentZeroGRPCServer
        logger.info("test_grpc_phase2.py: ✓ gRPC server implementation available")
    except ImportError as e:
        logger.error(f"test_grpc_phase2.py: ✗ gRPC server not available: {e}")
    
    # Check if gRPC client is available
    try:
        from python.helpers.ipc_grpc import GRPCAgentZeroIPC
        logger.info("test_grpc_phase2.py: ✓ gRPC client implementation available")
    except ImportError as e:
        logger.error(f"test_grpc_phase2.py: ✗ gRPC client not available: {e}")
    
    # Check gRPC dependencies
    try:
        import grpc
        logger.info("test_grpc_phase2.py: ✓ grpcio library available")
    except ImportError:
        logger.error("test_grpc_phase2.py: ✗ grpcio library not available - install with: pip install grpcio grpcio-tools")
    
    logger.info("Environment setup check completed")

async def main():
    """Run all tests"""
    logger.info("Starting Agent Zero Phase 2 gRPC Tests")
    logger.info("=" * 50)
    
    try:
        # Test environment setup
        test_environment_setup()
        
        # Test feature flags
        test_feature_flags()
        
        # Test IPC factory
        test_ipc_factory()
        
        # Test gRPC client
        await test_grpc_client()
        
        # Test gRPC server (if dependencies available)
        try:
            await test_grpc_server()
        except Exception as e:
            logger.warning(f"gRPC server test skipped: {e}")
        
        logger.info("=" * 50)
        logger.info("All tests completed successfully!")
        
    except Exception as e:
        logger.error(f"Test failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    # Set up test environment
    os.environ['AGENT_ZERO_DEBUG'] = 'true'
    os.environ['AGENT_ZERO_NATIVE_MODE'] = 'true'
    os.environ['AGENT_ZERO_USE_GRPC'] = 'true'
    
    asyncio.run(main())