FROM tiangolo/uvicorn-gunicorn-fastapi:python3.11

ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install Python dependencies
COPY ./requirements.txt /app/.
RUN pip install --default-timeout=100 --retries=5 -r requirements.txt

# Return to app directory and copy source code
COPY . /app

# Specify the port on which the container should listen
EXPOSE 4001

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "4001"]
