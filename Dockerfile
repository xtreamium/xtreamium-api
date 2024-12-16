FROM python:3.12.3
WORKDIR /code
COPY ./requirements.txt /app/requirements.txt
RUN mkdir /data
RUN pip install --upgrade pip
RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt
COPY ./app /app
WORKDIR /app
ENV PYTHONPATH=/
CMD ["uvicorn", "main:app", "--proxy-headers", "--host", "0.0.0.0", "--port", "80"]
