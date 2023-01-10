# Add a new comment to trigger build.
# Add a new comment to trigger build.
FROM python:3.9
COPY requirements.txt /requirements.txt
RUN pip install -r requirements.txt
COPY app.py /app.py
COPY authorization.py /authorization.py
COPY validation.py /validation.py
COPY  ./compose/apidocs/docker-entrypoint.d/40-merge-global-config.sh /40-merge-global-config.sh 
CMD ["python", "app.py"]
