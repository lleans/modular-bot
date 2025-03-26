# Stage 1: Build stage
FROM python:3.12-alpine as builder
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Compile bytecode & System Python
ENV UV_COMPILE_BYTECODE=1 UV_SYSTEM_PYTHON=1

# Define build argument
ARG INSTALL_BUILD_TOOLS=false

# Install build dependencies conditionally
RUN apk update && \
    apk add --no-cache git && \
    if [ "$INSTALL_BUILD_TOOLS" = "true" ]; then \
    apk add --no-cache build-base libffi-dev; \
    fi

# Change the working directory to the `app` directory
WORKDIR /app

# Install dependencies
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv pip install --strict -r pyproject.toml

# Copy the project into the intermediate image
ADD . /app

# Sync the project
RUN --mount=type=cache,target=/root/.cache/uv \
    uv pip install --strict -e .

# Stage 2: Runtime stage
FROM python:3.12-alpine
WORKDIR /app

# Create group and user "app"
RUN addgroup -S app && adduser -S -G app app

# Copy the application & necessary file from the builder
COPY --from=builder --chown=app:app /usr/local /usr/local
COPY --from=builder --chown=app:app /app/*.py .
COPY --from=builder --chown=app:app /app/ModularBot ./ModularBot

# Switch to non-root user
USER app

CMD ["python3", "bot.py"]
