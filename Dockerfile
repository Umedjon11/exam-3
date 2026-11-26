FROM python:3.14.2-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /exam-3

COPY requirements.txt /exam-3/
RUN pip install --no-cache-dir -r requirements.txt gunicorn

COPY . .

CMD ["pythoon", "manage.py", "runserver", "0.0.0.0:8000"]