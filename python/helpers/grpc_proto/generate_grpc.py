#!/usr/bin/env python3
"""
Script to generate gRPC Python code from proto files
"""

import os
import subprocess
import sys
from pathlib import Path

def generate_grpc_code():
    """Generate Python gRPC code from proto files"""
    
    # Get the directory containing this script
    script_dir = Path(__file__).parent
    proto_file = script_dir / "agent_zero.proto"
    
    if not proto_file.exists():
        print(f"Error: Proto file not found: {proto_file}")
        return False
    
    # Output directory for generated files
    output_dir = script_dir
    
    # Command to generate gRPC code
    cmd = [
        sys.executable, "-m", "grpc_tools.protoc",
        f"--proto_path={script_dir}",
        f"--python_out={output_dir}",
        f"--grpc_python_out=import_prefix=python.helpers.grpc_proto/:{output_dir}",
        str(proto_file)
    ]
    
    print(f"Generating gRPC code from {proto_file}")
    print(f"Command: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("gRPC code generation successful!")
        
        # List generated files
        generated_files = [
            output_dir / "agent_zero_pb2.py",
            output_dir / "agent_zero_pb2_grpc.py"
        ]
        
        for file_path in generated_files:
            if file_path.exists():
                print(f"Generated: {file_path}")
            else:
                print(f"Warning: Expected file not found: {file_path}")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"Error generating gRPC code: {e}")
        print(f"stdout: {e.stdout}")
        print(f"stderr: {e.stderr}")
        return False
    except FileNotFoundError:
        print("Error: grpc_tools not found. Install with: pip install grpcio-tools")
        return False

def create_init_file():
    """Create __init__.py file for the grpc_proto package"""
    init_file = Path(__file__).parent / "__init__.py"
    
    init_content = '''"""
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
'''
    
    with open(init_file, 'w') as f:
        f.write(init_content)
    
    print(f"Created: {init_file}")

if __name__ == "__main__":
    print("Agent Zero gRPC Code Generator")
    print("=" * 40)
    
    # Create __init__.py file
    create_init_file()
    
    # Generate gRPC code
    success = generate_grpc_code()
    
    if success:
        print("\nSuccess! gRPC code generation completed.")
        print("\nNext steps:")
        print("1. Install required dependencies: pip install grpcio grpcio-tools")
        print("2. Import the generated modules in your code")
        print("3. Implement the gRPC server and client")
    else:
        print("\nFailed to generate gRPC code. Please check the errors above.")
        sys.exit(1)