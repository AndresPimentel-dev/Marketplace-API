FROM python:3.11

WORKDIR /app

COPY requirements.txt .
# no olvidar poner -r ya que significa lea he instale
RUN pip install -r requirements.txt

COPY . .

CMD [ "uvicorn", "app.main:app", "--host", "0.0.0.0", "--reload" ]