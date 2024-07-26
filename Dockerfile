FROM python:3.12-alpine

# Install git
RUN apk update && \
    apk add --no-cache \
    build-base \
    libffi-dev \
    git

COPY . /app
WORKDIR /app

RUN pip install --upgrade pip
RUN pip install -U -r requirements.txt --no-dependencies

CMD ["python", "bot.py"]