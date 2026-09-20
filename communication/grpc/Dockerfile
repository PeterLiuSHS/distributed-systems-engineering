FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Generate gRPC code and fix imports
RUN mkdir -p generated && \
    python -m grpc_tools.protoc -Iproto \
        --python_out=generated \
        --grpc_python_out=generated \
        proto/user_service.proto && \
    # Make generated a proper Python package
    touch generated/__init__.py && \
    # Fix import issue in generated code
    sed -i 's/^import user_service_pb2/from . import user_service_pb2/' generated/user_service_pb2_grpc.py

# Expose gRPC port
EXPOSE 50052

# Start the gRPC server
CMD ["python", "server.py"]