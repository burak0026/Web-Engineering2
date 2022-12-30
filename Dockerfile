# Add a new comment to trigger build.
FROM python:3.9
RUN pip install -r requirements.txt
CMD ["python", "app.py"]
