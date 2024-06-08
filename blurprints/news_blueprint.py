import os
from uuid import uuid4
from pathlib import Path

from models.news_model import db, News, NewsImage
from models.responses import Response
from utiles.api_helper import api_input_get, api_input_check

from flask import Blueprint, request, send_file

news_blueprint = Blueprint('news', __name__)


@news_blueprint.route('', methods=['GET'])
def get_newses():
    """
    get newses
    ---
    tags:
      - news
    responses:
      200:
        description: get newses successfully
        schema:
          id: newses
          properties:
            description:
              type: string
            response:
              type: array
              items:
                properties:
                  id:
                    type: integer
                  news_title:
                    type: string
                  news_sub_title:
                    type: string
                  news_content:
                    type: string
                  created_time:
                    type: string
                  updated_time:
                    type: string
      404:
        description: news not found
    """
    news = News.query.all()
    return Response.response('get newses successfully', [n.to_dict() for n in news])


@news_blueprint.route('/<news_id>', methods=['GET'])
def get_news(news_id):
    """
    get news
    ---
    tags:
      - news
    parameters:
      - in: path
        name: news_id
        required: true
        type: integer
    responses:
      200:
        description: get news successfully
        schema:
          id: news
          properties:
            id:
              type: integer
            news_title:
              type: string
            news_sub_title:
              type: string
            news_content:
              type: string
            created_time:
              type: string
            updated_time:
              type: string
      404:
        description: news not found
    """
    news = News.query.get(news_id)
    if not news:
        return Response.not_found('news not found')

    return Response.response('get news successfully', news.to_dict())


@news_blueprint.route('', methods=['POST'])
def post_news():
    """
    post news
    ---
    tags:
      - news
    parameters:
      - in: body
        name: news
        required: true
        schema:
          id: news_input
          properties:
            news_title:
              type: string
            news_sub_title:
              type: string
            news_content:
              type: string
    responses:
      200:
        description: post news successfully
        schema:
          id: news
      400:
        description: no ['news_title', 'news_subtitle', 'news_content'] in request
    """
    if not api_input_check(['news_title', 'news_sub_title', 'news_content'], request.json):
        return Response.client_error("no ['news_title', 'news_sub_title', 'news_content'] in request")

    news = News(
        news_title=request.json['news_title'],
        news_sub_title=request.json['news_sub_title'],
        news_content=request.json['news_content']
    )

    db.session.add(news)
    db.session.commit()
    return Response.response('post news successfully', news.to_dict())


@news_blueprint.route('/<news_id>', methods=['PATCH'])
def patch_news(news_id):
    """
    patch news
    ---
    tags:
      - news
    parameters:
      - in: path
        name: news_id
        required: true
        type: integer
      - in: body
        name: news
        required: true
        schema:
          id: news_input
    responses:
      200:
        description: patch news successfully
        schema:
          id: news
      404:
        description: news not found
    """
    news = News.query.get(news_id)
    if not news:
        return Response.not_found('news not found')

    if 'news_title' in request.json:
        news.news_title = request.json['news_title']
    if 'news_sub_title' in request.json:
        news.news_sub_title = request.json['news_sub_title']
    if 'news_content' in request.json:
        news.news_content = request.json['news_content']

    db.session.commit()
    return Response.response('patch news successfully', news.to_dict())


@news_blueprint.route('/<news_id>', methods=['DELETE'])
def delete_news(news_id):
    """
    delete news
    ---
    tags:
      - news
    parameters:
      - in: path
        name: news_id
        required: true
        type: integer
    responses:
      200:
        description: delete news successfully
        schema:
          id: news
      404:
        description: news not found
    """
    news = News.query.get(news_id)
    if not news:
        return Response.not_found('news not found')

    db.session.delete(news)
    db.session.commit()
    return Response.response('delete news successfully', news.to_dict())


@news_blueprint.route('/image', methods=['GET'])
def get_news_images():
    """
    get news images
    ---
    tags:
      - news_image
    responses:
      200:
        description: get news images successfully
        schema:
          id: news_images
          properties:
            description:
              type: string
            response:
              type: array
              items:
                properties:
                  id:
                    type: integer
                  image_uuid:
                    type: string
                  image_name:
                    type: string
                  image_path:
                    type: string
                  created_time:
                    type: string
                  updated_time:
                    type: string
      404:
        description: news images not found
    """
    news_images = NewsImage.query.all()
    return Response.response('get news images successfully', [ni.to_dict() for ni in news_images])


@news_blueprint.route('/image/<news_image_uuid>', methods=['GET'])
def get_news_image(news_image_uuid):
    """
    get news image
    ---
    tags:
      - news_image
    parameters:
      - in: path
        name: news_image_uuid
        required: true
        type: string
    responses:
      200:
        description: get news image successfully
      404:
        description: news image not found
    """
    news_image = NewsImage.query.filter_by(image_uuid=news_image_uuid).first()
    if not news_image:
        return Response.not_found('news image not found')

    return send_file(news_image.image_path)


@news_blueprint.route('/image', methods=['POST'])
def post_news_image():
    """
    post news image
    ---
    tags:
      - news_image
    parameters:
      - in: formData
        name: image
        type: file
        required: true
    responses:
      200:
        description: post news image successfully
        schema:
          id: news_image
          properties:
            description:
              type: string
            response:
              properties:
                id:
                  type: integer
                image_uuid:
                  type: string
                image_name:
                  type: string
                image_path:
                  type: string
                created_time:
                  type: string
                updated_time:
                  type: string
      400:
        description: no image in request
    """
    image = request.files['image']
    image_uuid = uuid4().hex
    image_name = image.filename
    image_path = Path().cwd() / f'statics/images/{image_uuid}.{image_name.split(".")[-1]}'
    image.save(image_path)

    news_image = NewsImage(
        image_uuid=image_uuid,
        image_name=image_name,
        image_path=str(image_path)
    )

    db.session.add(news_image)
    db.session.commit()
    return Response.response('post news image successfully', news_image.to_dict())


@news_blueprint.route('/image/<news_image_uuid>', methods=['DELETE'])
def delete_news_image(image_uuid):
    """
    delete news image
    ---
    tags:
      - news_image
    parameters:
      - in: path
        name: news_image_uuid
        required: true
        type: string
    responses:
      200:
        description: delete news image successfully
        schema:
          id: news_image
      404:
        description: news image not found
    """
    news_image = NewsImage.query.filter_by(image_uuid=image_uuid).first()
    if not news_image:
        return Response.not_found('news image not found')

    os.remove(news_image.image_path)
    db.session.delete(news_image)
    db.session.commit()
    return Response.response('delete news image successfully', news_image.to_dict())
