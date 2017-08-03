FROM python:3

RUN pip install flask requests

COPY main.py .

ENV FLASK_APP=main.py

CMD ["python", "-m", "flask", "run", "--host=0.0.0.0"]