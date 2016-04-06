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

RUN pip install numpy==1.7.1
RUN pip install scipy==0.13.3
RUN pip install matplotlib==1.3.1

COPY requirements.txt /requirements.txt
RUN pip install --no-cache-dir -r /requirements.txt

RUN git clone git://github.com/bayerj/arac.git /root/arac && \
    cd /root/arac/ && \
    sed -i "s/.*test.*//i" SConstruct && \
    scons && \
    cp libarac.so /usr/lib/ && \
    cd /root/

ENV PYTHONPATH=/root/arac/src/python
