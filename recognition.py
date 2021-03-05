from flask import Flask, request, abort
import urllib
import numpy as np
import cv2
import easyocr
import logging
from http import HTTPStatus
reader = easyocr.Reader(['ar','en'], gpu=False)
logger = logging.getLogger("ocr-image-api")
app = Flask(__name__)

def recognition(image):
    """

    :param image:
    :return:
    """
    results = []
    texts = reader.readtext(image, detail=0, paragraph=True)
    response = ""
    for text in texts:
        response = response + " " + text

    return response


@app.route('/ocr', methods=['GET', 'POST'])
def process():
    """
    received request from client and process the image
    :return: dict of width and points
    """
    try:
        if 'imageFile' not in request.files and 'imageFile[]' not in request.files:
            logger.warning("no image was found in request")
            return {
                       "error": "No file uploaded, image file is required"
                   }, HTTPStatus.BAD_REQUEST
        images = request.files.get('imageFile')
        if not images:
            images = request.files.getlist('imageFile[]')
            logger.info("multiple images found in request")
        else:
            logger.info("signel image found in request")
            images = [images]

        results = []
        for x in images:
            image_np = np.asarray(bytearray(x.stream.read()), dtype="uint8")
            image = cv2.imdecode(image_np, cv2.IMREAD_COLOR)
            results.append(recognition(image))
            logger.info("successfully processed one image")

        return {
                   "results": results
               }, HTTPStatus.OK
    except Exception as e:
        logger.error(e)
        return {
            "error": str(e)
        }, HTTPStatus.INTERNAL_SERVER_ERROR


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=2000)
