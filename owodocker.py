FROM python:3.9 # change if u got other

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "oworat.py"]