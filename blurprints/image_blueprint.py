import os
from uuid import uuid4
from pathlib import Path
from datetime import datetime
from models.image_model import db, Image
from utiles.api_helper import api_input_get, api_input_check
from models.responses import Response

from flask import Blueprint, request, send_file

image_blueprint = Blueprint('image', __name__)


@image_blueprint.route('', methods=['POST'])
def post_image():
    """
    post member image
    ---
    tags:
      - image
    parameters:
      - in: formData
        name: file
        type: file
        required: true
    responses:
      200:
        description: post image successfully
        schema:
          id: image
          properties:
            description:
              example: 'post image successfully'
              type: string
            response:
              properties:
                id:
                  example: 1
                  type: integer
                image_name:
                  example: 'image.jpg'
                  type: string
                update_time:
                  example: 'Tue, 06 Aug 2024 10:39:27 GMT'
                  type: string
                create_time:
                  example: 'Tue, 06 Aug 2024 10:39:27 GMT'
                  type: string
      400:
        description: no ['image'] or content in form
    """

    if not api_input_check(['file'], request.files):
        return Response.client_error("no ['file'] or content in form")

    image = request.files['file']
    image_uuid = uuid4().hex
    image_name = image.filename
    image_path = f'./statics/images/{image_uuid}.{image_name.split(".")[-1]}'
    image.save(image_path)

    image = Image(image_name=image_name, image_path=str(image_path))
    db.session.add(image)
    db.session.commit()
    return Response.jodit_post_one(str(image.id))


@image_blueprint.route('<image_id>', methods=['GET'])
def get_image(image_id):
    """
    get image
    ---
    tags:
      - image
    parameters:
      - in: path
        name: image_id
        type: integer
        required: true
    responses:
      200:
        description: get image successfully
      404:
        description: image_id not exist
    """
    image = Image.query.get(image_id)
    if not image:
        return Response.not_found('image not exist')

    return send_file(image.image_path)


@image_blueprint.route('', methods=['GET'])
def get_images():
    """
    get member images
    ---
    tags:
      - image
    responses:
      200:
        description: get images successfully
        schema:
          id: images
          properties:
            description:
              type: string
            response:
              type: array
              items:
                properties:
                  id:
                    example: 1
                    type: integer
                  image_name:
                    example: 'image.jpg'
                    type: string
                  update_time:
                    example: 'Tue, 06 Aug 2024 10:39:27 GMT'
                    type: string
                  create_time:
                    example: 'Tue, 06 Aug 2024 10:39:27 GMT'
                    type: string
    """
    images = Image.query.all()
    return Response.jodit_get_all([image.to_dict() for image in images])


@image_blueprint.route('', methods=['DELETE'])
def delete_image():
    """
    delete image
    ---
    tags:
      - image
    parameters:
      - in: body
        name: name
        type: integer
        required: true
    responses:
      200:
        description: delete image successfully
      404:
        description: image_id not exist
    """

    image = Image.query.get(request.json['name'])
    if not image:
        return Response.not_found('image not exist')

    os.remove(image.image_path)
    db.session.delete(image)
    db.session.commit()
    return Response.response('delete image successfully')
