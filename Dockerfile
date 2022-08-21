FROM python:3.9

# Make working directories 
RUN  mkdir -p  /recommendation-system
WORKDIR  /recommendation-system

# 
COPY ./requirements.txt .

# install libraries
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# copy source code
COPY ./backend /recommendation-system/backend

# start backend
WORKDIR  /recommendation-system/backend 
CMD ["python", "main.py"]
# CMD ["uvicorn", "app.main:app", "--proxy-headers", "--host", "0.0.0.0", "--port", "8080"]


# EOF