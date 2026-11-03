# 1. Official lightweight Python 3.11
FROM python:3.11-slim

# 2. Set working folder inside container
WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 3. Install packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Copy all project files
COPY . .

# 5. Make startup script executable
RUN chmod +x start.sh

# 6. Start the app
CMD ["./start.sh"]