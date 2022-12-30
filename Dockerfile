# Add a new comment to trigger build.
FROM python:3.9
COPY requirements.txt /requirements.txt
RUN pip install -r requirements.txt
CMD ["python", "app.py"]
