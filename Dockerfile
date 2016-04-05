FROM python:2.7

RUN apt-get update && apt-get install -y \
        gcc \
        gettext \
        mysql-client libmysqlclient-dev \
        postgresql-client libpq-dev \
        sqlite3 \
        libblas-dev \
        liblapack-dev \
        libatlas-base-dev \
        gfortran \
        cron \
        swig \
    --no-install-recommends && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /requirements.txt
RUN pip install --no-cache-dir -r /requirements.txt

RUN git clone git://github.com/bayerj/arac.git /root/arac && \
    cd /root/arac/ && \
    sed -i "s/.*test.*//i" SConstruct && \
    scons && \
    cp libarac.so /usr/lib/ && \
    cd /root/

ENV PYTHONPATH=/root/arac/src/python
