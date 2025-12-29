# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Install cron
RUN apt-get update && apt-get install -y cron && rm -rf /var/lib/apt/lists/*

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Create crontab file
RUN echo "0 12 * * 1 /usr/local/bin/python /app/main.py" > /etc/cron.d/notificar-rcas

# Give execution rights on the cron job
RUN chmod 0644 /etc/cron.d/notificar-rcas

# Apply cron job
RUN crontab /etc/cron.d/notificar-rcas

# Run the cron daemon in foreground
CMD ["cron", "-f"]