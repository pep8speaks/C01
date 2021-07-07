# HTTP server + Django application
FROM python:3.7

# Install Python and Package Libraries
RUN apt-get update && apt-get upgrade -y && \
    apt-get autoremove && \
    apt-get autoclean && \
    apt-get install -f

RUN apt-get update && apt-get install -y default-jre postgresql postgresql-client gcc musl-dev

# Don't create bytecode files
ENV PYTHONDONTWRITEBYTECODE 1
# Don't buffer output
ENV PYTHONUNBUFFERED 1

# Create the django user
ENV HOME=/home/django
RUN useradd --create-home --home-dir $HOME django
RUN chown -R django:django $HOME

# Create the appropriate directories
ENV APP_HOME=/home/django/C01
RUN mkdir $APP_HOME
RUN mkdir $APP_HOME/staticfiles
WORKDIR $APP_HOME

COPY requirements.txt .
COPY *.py ./
COPY src src
COPY main main
COPY interface interface
COPY crawlers crawlers

RUN mkdir logs

# Copy the env file for Django
COPY docker-web/.env.prod interface/.env

ENV EXECUTION_TYPE=distributed
RUN python3 install.py

RUN mkdir /data
RUN chown django:django /data

# Install gunicorn for integration with Nginx
RUN pip install gunicorn

# Copy the gunicorn configuration file
COPY docker-web/gunicorn.conf.py ./gunicorn.conf.py

# Copy the kafka interface files
COPY kafka_interface kafka_interface
COPY docker-web/django_run.sh ./django_run.sh
RUN chmod +x django_run.sh

RUN chown -R django:django $APP_HOME
USER django

RUN python3 manage.py collectstatic --no-input --clear
