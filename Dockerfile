FROM python:3.10-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    POETRY_VERSION=1.7.1 \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1 \
    PIP_DEFAULT_TIMEOUT=360

# Set working directory
WORKDIR /home
RUN mkdir -p /home/databases && chmod -R 777 /home/databases

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    # If your scraping or PDF reading requires these, for example:
    # poppler-utils \
    # libxml2-dev libxslt-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH="/root/.local/bin:$PATH"
RUN poetry config installer.parallel false

# Copy only the pyproject & lock first, for caching
COPY pyproject.toml poetry.lock ./

# Install dependencies (remove `--no-dev` if Scrapy is in dev-deps)
RUN poetry install --no-root --no-dev

# Copy the rest of your application
COPY config /home/config
COPY watgpt /home/watgpt

# Expose the port
EXPOSE 8000

# Default command (overridden by docker-compose for db_init, etc.)
CMD ["poetry", "run", "uvicorn", "watgpt.api:app", "--host", "0.0.0.0", "--port", "8000"]
