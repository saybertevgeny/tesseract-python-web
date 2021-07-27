from flask import Flask, render_template, request
from werkzeug.utils import secure_filename
import os
import sys
from PIL import Image
import pytesseract
import argparse
import cv2
from pdf2image import convert_from_path
import tempfile
import time
from pathlib import Path
import pika

__author__ = 'Rick Torzynski <ricktorzynski@gmail.com>'
__source__ = ''

app = Flask(__name__)
UPLOAD_FOLDER = './static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024
#app.config['TMP_PATH'] = "C:/work/askd/ocr-tesseract-docker/tmp"
app.config['TMP_PATH'] = "/tmp"


def ocrImage(filepath):
    # load the example image and convert it to grayscale
    image = cv2.imread(filepath)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # apply thresholding to preprocess the image
    gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]

    # apply median blurring to remove any blurring
    gray = cv2.medianBlur(gray, 3)

    # save the processed image in the /static/uploads directory
    cv2.imwrite(filepath, gray)

    # perform OCR on the processed image
    text = pytesseract.image_to_pdf_or_hocr(Image.open(filepath), lang="rus",extension='hocr')

    # remove the processed image
    os.remove(filepath)
    return text


@app.route("/")
def index():
    # print(os.environ['HOME'])
    rmq_parameters = pika.URLParameters("amqp://mqadmin:BrqTtAFs9@10.10.0.9:5672/")
    rmq_connection = pika.BlockingConnection(rmq_parameters)
    rmq_channel = rmq_connection.channel()
    method_frame, header_frame, body = rmq_channel.basic_get('askd.tesseract.osg')
    if method_frame:
        print(method_frame, header_frame, body)
        rmq_channel.basic_ack(method_frame.delivery_tag)
    else:
        print('No message returned')


@app.route("/about")
def about():
    return render_template("about.html")


@app.route('/uploader', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        f = request.files['file']
        current_pid_directory = os.path.join(app.config['TMP_PATH'], str(int(time.time())))
        Path(current_pid_directory).mkdir(parents=True, exist_ok=True)
        text = ""
        # create a secure filename
        filename = f.filename
        file_extension = os.path.splitext(filename)[1]
        filename_without_extension = os.path.splitext(filename)[0]
        if file_extension == ".pdf":
            # save pdf for parsing
            pdf_full_path = os.path.join(current_pid_directory, filename)
            f.save(pdf_full_path)
            f.close()
            pages = convert_from_path(pdf_full_path, 500, fmt="jpeg")
            index = 0
            for page in pages:
                page_file_path = os.path.join(current_pid_directory, str(index)+".jpg")
                page.save(page_file_path)
                text += ocrImage(page_file_path)
                index += 1
            os.remove(pdf_full_path)
            os.rmdir(current_pid_directory)
        else:
            # save file to /static/uploads
            filepath = os.path.join(current_pid_directory, filename)
            f.save(filepath)
            # запустить функцию
            test = ocrImage(filepath)

        return render_template("uploaded.html", displaytext=text, fname=filename)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
