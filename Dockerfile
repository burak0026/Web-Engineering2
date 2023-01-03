# Add a new comment to trigger build.
# Add a new comment to trigger build.
FROM python:3.9
COPY requirements.txt /requirements.txt
COPY app.py /app.py
COPY  ./compose/apidocs/docker-entrypoint.d/40-merge-global-config.sh /40-merge-global-config.sh 
RUN pip install -r requirements.txt
CMD ["python", "app.py"]
