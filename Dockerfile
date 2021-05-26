# C01 Standalone
FROM python:3.7

# Install Python and Package Libraries
RUN apt-get update && apt-get upgrade -y && apt-get autoremove && apt-get autoclean
RUN apt-get install -y default-jre

COPY requirements.txt .
COPY *.py ./
COPY src src
COPY main main
COPY interface interface
COPY crawlers crawlers

EXPOSE 8000
RUN python install.py

ENTRYPOINT ["python", "manage.py", "runserver", "0.0.0.0:8000", "--noreload"]
