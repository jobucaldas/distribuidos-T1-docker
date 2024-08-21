FROM python:3
ENV PYTHONUNBUFFERED 1

WORKDIR /app

RUN pip install Flask Flask-Cors
COPY flask-backend/app.py main.py

CMD ["python", "main.py"]