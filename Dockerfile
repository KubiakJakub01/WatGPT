FROM python:3.10-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    POETRY_VERSION=1.7.1 \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1 \
    PIP_DEFAULT_TIMEOUT=360

# Set working directory
WORKDIR /home

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH="/root/.local/bin:$PATH"

RUN poetry config installer.parallel false

# Copy only necessary files for dependency installation
COPY pyproject.toml poetry.lock ./

# Install dependencies
RUN poetry install --no-root --no-dev

# Copy the rest of the application
COPY config /home/config
COPY watgpt /home/watgpt

# Expose the port
EXPOSE 8000

# Run the FastAPI app
CMD ["poetry", "run", "uvicorn", "watgpt.api:app", "--host", "0.0.0.0", "--port", "8000"]
