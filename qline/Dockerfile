# 1. Start with a lean Python base image
FROM python:3.11-slim

# 2. Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 3. Set the working directory inside the container
WORKDIR /app

# 4. Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copy your entire project code into the container
COPY . .

# 6.Run collectstatic to gather all static files
RUN python manage.py collectstatic --noinput

# 7. Expose the port Gunicorn will run on
EXPOSE 8000

# 8. Run your app
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "qline.wsgi:application"]
