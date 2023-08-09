FROM python:3.10
RUN apt-get update
RUN mkdir /app
ENV TZ="Europe/Moscow"
RUN date
WORKDIR /app
COPY . /app
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
CMD ["python", "./main.py"]
