import logging
from typing import Optional
from .ipc_interface import AbstractAgentZeroIPC
from .ipc_mock import MockAgentZeroIPC
from .ipc_legacy_wrapper import LegacyRFCWrapper
from .feature_flags import FeatureFlags

# Import gRPC IPC with fallback
try:
    from .ipc_grpc import GRPCAgentZeroIPC
    GRPC_AVAILABLE = True
except ImportError as e:
    logger = logging.getLogger(__name__)
    logger.warning(f"gRPC IPC not available: {e}")
    GRPC_AVAILABLE = False
    GRPCAgentZeroIPC = None

logger = logging.getLogger(__name__)

class IPCFactory:
    """Factory for creating appropriate IPC implementation"""
    
    _instance: Optional[AbstractAgentZeroIPC] = None
    _instance_type: Optional[str] = None
    
    @staticmethod
    def create_ipc() -> AbstractAgentZeroIPC:
        """Create the appropriate IPC implementation based on environment"""
        
        if FeatureFlags.is_native_mode() and FeatureFlags.use_grpc_ipc():
            # Native mode with gRPC requested
            if GRPC_AVAILABLE and GRPCAgentZeroIPC is not None:
                logger.info("Creating gRPC IPC for native mode")
                logger.info("Full-featured native mode with gRPC communication")
                return GRPCAgentZeroIPC()
            else:
                logger.warning("gRPC IPC requested but not available, falling back to Mock IPC")
                logger.info("Install grpcio and grpcio-tools for gRPC support")
                return MockAgentZeroIPC()
        
        elif FeatureFlags.is_native_mode():
            # Native mode with mock IPC (Phase 1 behavior)
            logger.info("Creating Mock IPC for native mode")
            logger.info("File operations will execute locally with mock fallbacks")
            return MockAgentZeroIPC()
        
        elif FeatureFlags.use_grpc_ipc():
            # Docker mode with gRPC requested - fall back to legacy
            logger.info("gRPC IPC requested in Docker mode, falling back to Legacy RFC wrapper")
            return LegacyRFCWrapper()
        
        else:
            # Standard Docker mode
            logger.info("Creating Legacy RFC wrapper for Docker mode")
            return LegacyRFCWrapper()
    
    @staticmethod
    def get_ipc() -> AbstractAgentZeroIPC:
        """Get singleton IPC instance"""
        current_mode = IPCFactory._get_current_mode()
        
        # Check if we need to recreate the instance due to mode change
        if (IPCFactory._instance is None or 
            IPCFactory._instance_type != current_mode):
            
            if IPCFactory._instance is not None:
                logger.info(f"IPC mode changed from {IPCFactory._instance_type} to {current_mode}")
                IPCFactory._instance.cleanup()
            
            IPCFactory._instance = IPCFactory.create_ipc()
            IPCFactory._instance_type = current_mode
            
            logger.info(f"IPC initialized: {IPCFactory._instance.get_mode_name()}")
            
            # Log health status if debug mode is enabled
            if FeatureFlags.is_debug_mode():
                health = IPCFactory._instance.get_health_status()
                logger.debug(f"IPC Health Status: {health}")
        
        return IPCFactory._instance
    
    @staticmethod
    def reset_ipc():
        """Reset IPC instance (useful for testing or configuration changes)"""
        if IPCFactory._instance is not None:
            logger.info(f"Resetting IPC instance: {IPCFactory._instance.get_mode_name()}")
            IPCFactory._instance.cleanup()
        
        IPCFactory._instance = None
        IPCFactory._instance_type = None
        logger.info("IPC instance reset completed")
    
    @staticmethod
    def get_health_status() -> dict:
        """Get comprehensive health status of the current IPC instance"""
        try:
            ipc = IPCFactory.get_ipc()
            health = ipc.get_health_status()
            
            # Add factory-level information
            health.update({
                'factory_info': {
                    'current_mode': IPCFactory._get_current_mode(),
                    'instance_type': IPCFactory._instance_type,
                    'singleton_active': IPCFactory._instance is not None
                },
                'environment': {
                    'native_mode': FeatureFlags.is_native_mode(),
                    'grpc_requested': FeatureFlags.use_grpc_ipc(),
                    'debug_mode': FeatureFlags.is_debug_mode(),
                    'fallback_enabled': FeatureFlags.should_fallback_to_local(),
                    'rfc_host': FeatureFlags.get_rfc_host(),
                    'rfc_port': FeatureFlags.get_rfc_port(),
                    'ipc_timeout': FeatureFlags.get_ipc_timeout()
                }
            })
            
            return health
            
        except Exception as e:
            logger.error(f"Failed to get IPC health status: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'factory_info': {
                    'current_mode': IPCFactory._get_current_mode(),
                    'instance_type': IPCFactory._instance_type,
                    'singleton_active': IPCFactory._instance is not None
                }
            }
    
    @staticmethod
    def _get_current_mode() -> str:
        """Get the current mode string for comparison"""
        if FeatureFlags.is_native_mode() and FeatureFlags.use_grpc_ipc():
            return "native_grpc"
        elif FeatureFlags.is_native_mode():
            return "native_mock"
        elif FeatureFlags.use_grpc_ipc():
            return "grpc"
        else:
            return "legacy_rfc"
    
    @staticmethod
    def is_ipc_available() -> bool:
        """Check if IPC is available and functional"""
        try:
            ipc = IPCFactory.get_ipc()
            return ipc.is_connected()
        except Exception as e:
            logger.error(f"IPC availability check failed: {e}")
            return False
    
    @staticmethod
    def get_mode_info() -> dict:
        """Get information about the current IPC mode"""
        try:
            ipc = IPCFactory.get_ipc()
            return {
                'mode_name': ipc.get_mode_name(),
                'mode_type': IPCFactory._get_current_mode(),
                'connected': ipc.is_connected(),
                'available': True
            }
        except Exception as e:
            return {
                'mode_name': 'Unknown',
                'mode_type': IPCFactory._get_current_mode(),
                'connected': False,
                'available': False,
                'error': str(e)
            }