# ---------- Stage 1: Build + Tests ----------
FROM gcc:13 AS builder

WORKDIR /app

# Copy project sources
COPY include/ include/
COPY src/ src/
COPY tests/ tests/
COPY CMakeLists.txt .

# Install CMake for the build
RUN apt-get update && \
    apt-get install -y cmake && \
    rm -rf /var/lib/apt/lists/*

# Configure + build
RUN cmake -B build -S . -DCMAKE_BUILD_TYPE=Release && \
    cmake --build build --config Release

# Run unit tests inside the build container
RUN cd build && ctest --output-on-failure

# ---------- Stage 2: Runtime ----------
FROM gcc:13 AS runtime

WORKDIR /app

# Copy the built binary from the builder stage
COPY --from=builder /app/build/pricer_server ./pricer_server

# Default port
ENV PRICER_PORT=8080
EXPOSE 8080

# Start the server
CMD ["./pricer_server"]