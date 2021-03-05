from flask import Flask, request, abort
import urllib
import numpy as np
import cv2
import easyocr
import os
from http import HTTPStatus
reader = easyocr.Reader(['en'], gpu=False)

app = Flask(__name__)

def recognition(image):
    """

    :param image:
    :return:
    """
    results = []
    texts = reader.readtext(image)
    for (bbox, text, prob) in texts:
        output = {
            "coordinate": [list(map(float, coordinate)) for coordinate in bbox],
            "text": text,
            "score": prob
        }
        results.append(output)

    return results


@app.route('/ocr', methods=['GET', 'POST'])
def process():
    """
    received request from client and process the image
    :return: dict of width and points
    """
    try:
        if 'imageFile' not in request.files:
            return {
                       "error": "No file uploaded, image file is required"
                   }, HTTPStatus.BAD_REQUEST
        image = request.files['imageFile']
        image_np = np.asarray(bytearray(image.stream.read()), dtype="uint8")

        image = cv2.imdecode(image_np, cv2.IMREAD_COLOR)
        results = recognition(image)
        return {
                   "results": results
               }, HTTPStatus.OK
    except Exception as e:
        return {
            "error": str(e)
        }, HTTPStatus.INTERNAL_SERVER_ERROR


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=2000)
