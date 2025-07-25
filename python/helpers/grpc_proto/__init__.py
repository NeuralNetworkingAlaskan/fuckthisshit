"""
Agent Zero gRPC Protocol Buffer definitions and generated code
"""

# Import generated gRPC modules when available
try:
    from . import agent_zero_pb2
    from . import agent_zero_pb2_grpc
    
    __all__ = ['agent_zero_pb2', 'agent_zero_pb2_grpc']
    
except ImportError as e:
    print(f"Warning: gRPC modules not available: {e}")
    print("Run 'python generate_grpc.py' to generate gRPC code")
    __all__ = []
