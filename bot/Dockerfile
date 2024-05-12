FROM python:3

WORKDIR /bot

# Установка времени
RUN apt-get update && apt-get install -y \
    ca-certificates \
    tzdata \
 && rm -rf /var/lib/apt/lists/*

# Установка часового пояса
RUN ln -fs /usr/share/zoneinfo/Europe/Moscow /etc/localtime && dpkg-reconfigure -f noninteractive tzdata

COPY requirements.txt ./

# Установка PostgreSQL из официального репозитория Debian
RUN apt-get update && apt-get install -y \
    postgresql \
    postgresql-contrib \
    libpq-dev \
    python3-dev

RUN pip install -r requirements.txt

COPY . /bot


CMD ["python","main.py"]