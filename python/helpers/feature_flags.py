import os
from typing import Dict, Any, Optional

from .feature_flag_client import FeatureFlagClient

class FeatureFlags:
    """Centralized feature flag management for Agent Zero"""
    
    @staticmethod
    def is_native_mode() -> bool:
        """Check if running in native (non-Docker) mode"""
        return os.environ.get('AGENT_ZERO_NATIVE_MODE', 'false').lower() == 'true'
    
    @staticmethod
    def use_grpc_ipc() -> bool:
        """Check if gRPC IPC should be used instead of RFC"""
        remote = FeatureFlagClient.is_feature_enabled("use-grpc-ipc")
        if remote is not None:
            return remote
        return os.environ.get('AGENT_ZERO_USE_GRPC', 'false').lower() == 'true'
    
    @staticmethod
    def get_rfc_host() -> str:
        """Get RFC host (default localhost for native mode)"""
        return os.environ.get('AGENT_ZERO_RFC_HOST', 'localhost')
    
    @staticmethod
    def get_rfc_port() -> int:
        """Get RFC port (default 55080)"""
        return int(os.environ.get('AGENT_ZERO_RFC_PORT', '55080'))
    
    @staticmethod
    def get_log_level() -> str:
        """Get logging level"""
        return os.environ.get('AGENT_ZERO_LOG_LEVEL', 'INFO')
    
    @staticmethod
    def is_debug_mode() -> bool:
        """Check if debug mode is enabled"""
        return os.environ.get('AGENT_ZERO_DEBUG', 'false').lower() == 'true'
    
    @staticmethod
    def get_ipc_timeout() -> int:
        """Get IPC timeout in seconds"""
        return int(os.environ.get('AGENT_ZERO_IPC_TIMEOUT', '30'))
    
    @staticmethod
    def should_fallback_to_local() -> bool:
        """Check if should fallback to local execution on IPC failure"""
        return os.environ.get('AGENT_ZERO_FALLBACK_LOCAL', 'true').lower() == 'true'