# IPC Refactoring Framework

This document outlines a strategy for modernising Agent Zero's inter-process communication so it can run natively on Ubuntu without the legacy Docker based system.

## Why Replace the Legacy IPC?
- Custom IPC code has grown brittle and platform specific.
- Security features such as TLS are missing.
- Lack of a formal contract makes new development risky and error prone.

A modern IPC layer must be maintainable, scalable, performant and secure.

## gRPC vs ZeroMQ
| Feature | gRPC | ZeroMQ |
|---|---|---|
|Abstraction|High level RPC framework|Low level messaging library|
|Transport|HTTP/2|Custom TCP patterns|
|Serialization|Protocol Buffers|User defined|
|Security|Built in TLS|External libraries required|
|Load balancing|Native client support|Manual implementation|

Although ZeroMQ can be faster in synthetic benchmarks, gRPC's batteries‑included approach provides a better long term foundation and forces a clear contract via Protocol Buffers. Therefore gRPC is the recommended solution for Agent Zero.

## Migration Methodology (PIMF)
1. **Prepare** – map all existing IPC calls and create characterization tests. Introduce an adapter interface and dependency injection so that the old IPC can be swapped with minimal code changes.
2. **Implement** – build the gRPC stack. Define services in `.proto` files and generate the Python stubs. Create gRPC based adapters that implement the IPC interface.
3. **Migrate** – activate the new system gradually using a feature flag. Roll out in stages (CI, staging, canary, phased production) while monitoring metrics.
4. **Finalize** – once gRPC handles 100% of traffic, remove the legacy IPC code and update documentation.

## Operational Notes
- Use `asyncio` with grpcio's asynchronous API for high concurrency.
- Map internal errors to gRPC status codes and implement retries with backoff for transient failures.
- Enable TLS for service to service communication and propagate authentication data via metadata.
- In CI, lint `.proto` files and generate stubs as part of the build.

Following this framework will lead to a more robust, maintainable and secure communication layer for Agent Zero.
