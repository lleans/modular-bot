FROM python:3.12-alpine

# Define build argument
ARG INSTALL_BUILD_TOOLS=false

# Install dependencies conditionally
RUN apk update && \
    apk add --no-cache git && \
    if [ "$INSTALL_BUILD_TOOLS" = "true" ]; then \
    apk add --no-cache build-base libffi-dev; \
    fi

COPY . /app
WORKDIR /app

# Install Python dependencies
RUN pip install --upgrade pip
RUN pip install -U -r requirements.txt --no-dependencies

CMD ["python", "bot.py"]
