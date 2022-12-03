FROM python:3.10

WORKDIR /usr/src/app

COPY . /usr/src/app
RUN pip install --no-cache-dir -r requirements.txt


CMD ["python", "main.py"]
