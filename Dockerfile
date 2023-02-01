# Use an existing Python image as the base image
FROM python:3.8-alpine

# Give the label name
LABEL name="app"

# Set the working directory in the container
WORKDIR /app

# Copy the requirements.txt file to the container
COPY requirements.txt .

# Install the dependencies
RUN pip install -r requirements.txt

# Copy the rest of the code to the container
COPY . .

# Set the environment variable
ENV GOOGLE_API_KEY=AIzaSyBi4Y4V0EadlXkw5f9Nq6LFOXVodB-OmRg

# Command to run the appdocker run ubuntu ls
CMD ["flask", "run", "--host=0.0.0.0"]

