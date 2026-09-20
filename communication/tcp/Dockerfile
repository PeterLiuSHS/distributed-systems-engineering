# 1. Use the official lightweight Python 3.9 image
FROM python:3.9-slim

# 2. Set the working directory inside the container
WORKDIR /app

# 3. Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# 4. Copy all project files into the container
COPY . .

# 5. Expose the port the application is listening on (documentation only)
EXPOSE 8080

# 6. Set the default command to run server.py when container starts
CMD ["python", "server.py"]