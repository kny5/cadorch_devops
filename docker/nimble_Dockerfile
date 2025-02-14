FROM ubuntu:latest

# Install Linux dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-venv \
    python3-pip \
    git \
    curl \
    xvfb \
    x11-xserver-utils \
    openscad \
    fontconfig \
    mesa-utils \
    libgl1 \
    libgl1-mesa-dev \
    libglu1-mesa \
    libosmesa6 \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Clone the repository
RUN git clone https://github.com/Wakoma/nimble.git .

# Set up and activate virtual environment
ENV VIRTUAL_ENV=/app/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Install dependencies:
RUN pip install -e .
RUN pip install scad2gltf

# Use port 8000
EXPOSE 8000

# Set up environment for headless execution
ENV DISPLAY=:99

# Generate from hardcoded configuration options
RUN gen_nimble_conf_options

# Test using headless generator
RUN xvfb-run -a --server-args="-screen 0 1024x768x24" cadorchestrator --headless generate '{"device-ids": ["NUC10i5FNH", "Raspberry_Pi_4B", "Raspberry_Pi_4B"]}'

# Set server at 0.0.0.0:8000

COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh
CMD ["/app/entrypoint.sh"]
