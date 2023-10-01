FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

# Add deadsnakes PPA, install Python 3.10, and bedtools
RUN apt-get update && apt-get install -y \
    software-properties-common \
    bedtools && \
    add-apt-repository ppa:deadsnakes/ppa && \
    apt-get update && \
    apt-get install -y python3.10 python3.10-venv python3.10-dev python3-pip

WORKDIR /app

COPY ./requirements.txt /app
RUN pip3.10 install --no-cache-dir --upgrade -r requirements.txt

COPY . /app

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

# CMD ["python3.10", "manage.py", "runserver"]