# Agent Zero Native Mode Migration Guide

## Overview

This guide covers both Phase 1 and Phase 2 implementations of Agent Zero's RFC refactoring, enabling native Ubuntu deployment without Docker dependencies. Phase 1 provides a tactical bypass solution with mock functionality, while Phase 2 delivers a full-featured gRPC-based IPC system with complete feature parity to Docker mode.

## Architecture Changes

### Before (Docker-dependent RFC)
```
Agent Zero → RFC Client → HTTP Request → Docker Container → Function Execution
```

### After (IPC Abstraction - Phase 1 & 2)
```
Agent Zero → IPC Factory → [Mock IPC | Legacy RFC | gRPC IPC] → Function Execution
                                                        ↓
                                                   gRPC Server
                                                        ↓
                                              Advanced Operations
                                           (Files, Commands, Health)
```

## Environment Variables

### Native Mode Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `AGENT_ZERO_NATIVE_MODE` | `false` | Enable native mode (bypasses Docker RFC) |
| `AGENT_ZERO_USE_GRPC` | `false` | Use gRPC instead of legacy RFC (Phase 2) |
| `AGENT_ZERO_GRPC_HOST` | `localhost` | gRPC server host (Phase 2) |
| `AGENT_ZERO_GRPC_PORT` | `50051` | gRPC server port (Phase 2) |
| `AGENT_ZERO_GRPC_CERT` | *(empty)* | TLS certificate path |
| `AGENT_ZERO_GRPC_KEY` | *(empty)* | TLS private key path |
| `AGENT_ZERO_GRPC_ROOT_CERT` | *(empty)* | Root CA for client auth |
| `AGENT_ZERO_RFC_HOST` | `localhost` | RFC server host (legacy) |
| `AGENT_ZERO_RFC_PORT` | `55080` | RFC server port (legacy) |
| `AGENT_ZERO_FALLBACK_LOCAL` | `true` | Fallback to local execution on IPC failure |
| `AGENT_ZERO_IPC_TIMEOUT` | `30` | IPC timeout in seconds |
| `AGENT_ZERO_LOG_LEVEL` | `INFO` | Logging level |
| `AGENT_ZERO_DEBUG` | `false` | Enable debug mode |

### Quick Setup

1. **Copy the native configuration template:**
   ```bash
   cp .env.native .env
   ```

2. **Add your API keys to `.env`:**
   ```bash
   # Add your actual API keys
   API_KEY_OPENAI=your_openai_key_here
   API_KEY_ANTHROPIC=your_anthropic_key_here
   # ... other keys
   ```

3. **Start Agent Zero in native mode:**
   ```bash
   python run_ui.py
   ```

## Deployment Modes

### 1. Docker Mode (Default - Unchanged)
- **Use case**: Full functionality, production deployments
- **Configuration**: `AGENT_ZERO_NATIVE_MODE=false`
- **Behavior**: Uses existing RFC system with Docker containers
- **Compatibility**: 100% backward compatible

### 2. Native Mock Mode
- **Use case**: Development, testing, quick setup
- **Configuration**: `AGENT_ZERO_NATIVE_MODE=true`
- **Behavior**: File operations execute locally with mock fallbacks
- **Limitations**: Some advanced features may have reduced functionality

### 3. Native gRPC Mode (Phase 2 - Available)
- **Use case**: Full native functionality without Docker
- **Configuration**: `AGENT_ZERO_NATIVE_MODE=true` + `AGENT_ZERO_USE_GRPC=true`
- **Behavior**: High-performance gRPC communication with complete feature parity
- **Requirements**: `pip install grpcio grpcio-tools`

## Key Components

### 1. Feature Flags (`python/helpers/feature_flags.py`)
Centralized configuration management for deployment modes.

### 2. IPC Interface (`python/helpers/ipc_interface.py`)
Abstract interface that all IPC implementations must follow.

### 3. Mock IPC (`python/helpers/ipc_mock.py`)
Mock implementation for native mode with local execution and fallbacks.

### 4. Legacy RFC Wrapper (`python/helpers/ipc_legacy_wrapper.py`)
Wrapper around existing RFC system for backward compatibility.

### 5. IPC Factory (`python/helpers/ipc_factory.py`)
Factory pattern for creating appropriate IPC implementation based on environment.

## Functionality in Native Mode

### ✅ Working Features
- Basic agent interactions
- Local file operations
- Text processing and generation
- API calls to LLM providers
- Web UI access
- Settings management
- Memory and knowledge systems

### ⚠️ Limited Features
- Advanced file system operations (fallback to mock responses)
- System command execution (limited to host system)
- Container-specific tools and utilities

### ❌ Not Available
- Docker-specific functionality
- SSH access to containers
- Isolated execution environments

## Troubleshooting

### Common Issues

#### 1. "RFC functionality will be mocked" Warning
**Symptom**: Warning message on startup
```
⚠️  RFC functionality will be mocked - limited functionality expected
```
**Solution**: This is expected in native mode. For full functionality, use Docker mode.

#### 2. IPC Initialization Failures
**Symptom**: Error during IPC initialization
```
❌ Failed to initialize IPC: [error details]
```
**Solutions**:
- Check environment variables are set correctly
- Verify Python dependencies are installed
- Check file permissions
- Review logs for specific error details

#### 3. File Operation Failures
**Symptom**: File operations returning mock responses
**Solutions**:
- Ensure `AGENT_ZERO_FALLBACK_LOCAL=true`
- Check file system permissions
- Verify paths are accessible
- Review debug logs with `AGENT_ZERO_DEBUG=true`

#### 4. Performance Issues
**Symptom**: Slow response times in native mode
**Solutions**:
- Increase `AGENT_ZERO_IPC_TIMEOUT`
- Enable debug mode to identify bottlenecks
- Check system resources
- Consider using Docker mode for better performance

### Debug Mode

Enable comprehensive debugging:
```bash
export AGENT_ZERO_DEBUG=true
export AGENT_ZERO_LOG_LEVEL=DEBUG
python run_ui.py
```

### Health Check

Check IPC system health programmatically:
```python
from python.helpers.ipc_factory import IPCFactory

# Get health status
health = IPCFactory.get_health_status()
print(health)

# Check if IPC is available
available = IPCFactory.is_ipc_available()
print(f"IPC Available: {available}")
```

### Log Analysis

Key log messages to monitor:

#### Startup Messages
```
🚀 Starting Agent Zero in NATIVE MODE
✅ IPC initialized: Mock (Native)
```

#### Function Calls
```
MOCK IPC: Executing python.helpers.files.read_file locally
MOCK IPC SYNC: Executing python.helpers.files.write_file locally
```

#### Fallback Operations
```
RFC failed, attempting local execution for function_name
Local execution successful for function_name
```

## Migration Checklist

### Pre-Migration
- [x] Backup existing configuration
- [x] Document current Docker setup
- [x] Test current functionality
- [x] Prepare API keys and credentials

### Migration Steps
- [x] Copy `.env.native` to `.env`
- [x] Configure API keys
- [x] Set `AGENT_ZERO_NATIVE_MODE=true`
- [x] Test startup with `python run_ui.py`
- [x] Verify basic functionality
- [x] Monitor logs for issues

### Post-Migration
- [x] Test core agent features
- [x] Verify file operations work
- [x] Check web UI accessibility
- [x] Document any limitations encountered
- [x] Set up monitoring/logging

## Performance Considerations

### Native Mode Performance
- **Startup**: Faster (no Docker container initialization)
- **File Operations**: Direct filesystem access
- **Memory Usage**: Lower (no container overhead)
- **CPU Usage**: Varies (depends on local vs. container execution)

### Optimization Tips
1. Use SSD storage for better file I/O performance
2. Allocate sufficient RAM for local model loading
3. Configure appropriate timeout values
4. Monitor system resources during operation

## Security Considerations

### Native Mode Security
- **File System**: Direct access to host filesystem
- **Network**: Uses host network stack
- **Processes**: Runs with user permissions
- **Isolation**: No container isolation

### Security Best Practices
1. Run with minimal required permissions
2. Use dedicated user account for Agent Zero
3. Implement proper firewall rules
4. Monitor file system access
5. Regular security updates

## Rollback Procedure

To revert to Docker mode:

1. **Update environment:**
   ```bash
   export AGENT_ZERO_NATIVE_MODE=false
   ```

2. **Restart application:**
   ```bash
   python run_ui.py
   ```

3. **Verify Docker functionality:**
   - Check RFC connections
   - Test container operations
   - Verify full feature set

## Support and Resources

### Getting Help
1. Check this troubleshooting guide
2. Review application logs
3. Enable debug mode for detailed information
4. Check GitHub issues for similar problems

### Useful Commands
```bash
# Check IPC health
python -c "from python.helpers.ipc_factory import IPCFactory; print(IPCFactory.get_health_status())"

# Test native mode startup
AGENT_ZERO_NATIVE_MODE=true AGENT_ZERO_DEBUG=true python run_ui.py

# Reset IPC connection
python -c "from python.helpers.ipc_factory import IPCFactory; IPCFactory.reset_ipc()"
```

### File Locations
- Configuration: `.env`
- Logs: Check console output or configure logging
- IPC Components: `python/helpers/ipc_*.py`
- Feature Flags: `python/helpers/feature_flags.py`

## Phase 2 Implementation (Available)

### ✅ Completed Enhancements
- ✅ Full gRPC IPC implementation
- ✅ Enhanced native mode functionality with complete feature parity
- ✅ Performance optimizations with binary protocol
- ✅ Advanced file system and command execution operations
- ✅ Comprehensive testing suite

### Phase 2 Quick Start
```bash
# Install gRPC dependencies
pip install grpcio grpcio-tools

# Enable Phase 2 gRPC mode
export AGENT_ZERO_NATIVE_MODE=true
export AGENT_ZERO_USE_GRPC=true

# Start Agent Zero
python run_ui.py
```

### Phase 2 Testing
```bash
# Run comprehensive test suite
python python/helpers/test_grpc_phase2.py

# Check gRPC health status
python -c "
from python.helpers.ipc_factory import IPCFactory
health = IPCFactory.get_health_status()
print(f'Mode: {health[\"mode\"]}')
print(f'Connected: {health[\"connected\"]}')
"
```

---

**Note**: Phase 2 provides production-ready native Ubuntu deployment with full feature parity to Docker mode. Both Phase 1 (Mock) and Phase 2 (gRPC) native modes are available, with automatic fallback mechanisms ensuring reliable operation.