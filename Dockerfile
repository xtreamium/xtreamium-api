FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Copy and install dependencies
COPY pyproject.toml .
RUN pip install .

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Run migrations and start app
CMD ["sh", "-c", "alembic upgrade head && python app/main.py"]
