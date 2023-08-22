# Use the official Python 3.9 image
FROM python:3.9

# Set the working directory
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY requirements.txt /app/requirements.txt
COPY gunicorn_conf.py /app/gunicorn_conf.py

# Install dependencies
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy the application code
COPY . /app

# Set environment variables
ENV WEB_CONCURRENCY=1
ENV PYTHONUNBUFFERED=1

# Expose port 80 for Flask
EXPOSE 80

# Command to run the application
CMD ["gunicorn", "--conf", "gunicorn_conf.py", "--bind", "0.0.0.0:80", "main:app"]