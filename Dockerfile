FROM continuumio/anaconda3:latest

RUN apt-get update -y
#RUN apt-get install -y python-pip python-dev build-essential
#RUN apt update && apt install -y libsm6 libxext6


RUN apt-get -y install curl
RUN apt-get -y install tesseract-ocr
RUN apt-get -y install tesseract-ocr-rus
RUN apt-get -y install ffmpeg libsm6 libxext6
RUN apt-get install poppler-utils -y

COPY . /app
WORKDIR /app
RUN pip install pillow
RUN pip install pytesseract
RUN pip install opencv-contrib-python
RUN pip install numpy
RUN pip install pillow
RUN pip install pytesseract
RUN pip install MarkupSafe
RUN pip install -U Werkzeug==0.16.0
RUN pip install Jinja2>=2.10.1

RUN pip install certifi==2018.11.29
RUN pip install Click==7.0
RUN pip install Flask==1.0.2
RUN pip install gunicorn==19.9.0
RUN pip install itsdangerous==1.1.0
RUN pip install pdf2image
RUN pip install pika

#RUN pip install poppler
#RUN pip install -r requirements.txt#
#ENTRYPOINT ["python"]
#CMD ["app.py"]