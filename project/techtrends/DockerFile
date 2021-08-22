FROM python:2.7
COPY . /DockerTechTrends
WOKRDIR /DockerTechTrends
RUN pip install -r requirements.txt
RUN python init_db.py
EXPOSE 3111
CMD ["pyhon", "app.py"]