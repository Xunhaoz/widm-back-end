import os
from uuid import uuid4
from pathlib import Path

from sqlalchemy import desc

from models.news_model import db, News
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
                    example: 1
                    type: integer
                  title:
                    example: 'title'
                    type: string
                  sub_title:
                    example: 'sub_title'
                    type: string
                  content:
                    example: 'content'
                    type: string
                  created_time:
                    example: 'Tue, 06 Aug 2024 10:39:27 GMT'
                    type: string
                  updated_time:
                    example: 'Tue, 06 Aug 2024 10:39:27 GMT'
                    type: string
      404:
        description: news not found
    """
    news = db.session.query(News)
    news = news.order_by(desc(News.create_time)).all()
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
            description:
              type: string
            response:
              properties:
                id:
                  example: 1
                  type: integer
                title:
                  example: 'title'
                  type: string
                sub_title:
                  example: 'sub_title'
                  type: string
                content:
                  example: 'content'
                  type: string
                created_time:
                  example: 'Tue, 06 Aug 2024 10:39:27 GMT'
                  type: string
                updated_time:
                  example: 'Tue, 06 Aug 2024 10:39:27 GMT'
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
            title:
              example: 'title'
              type: string
            sub_title:
              example: 'sub_title'
              type: string
            content:
              example: 'content'
              type: string
    responses:
      200:
        description: post news successfully
        schema:
          id: news
      400:
        description: no ['title', 'sub_title', 'content'] in request
    """
    if not api_input_check(['title', 'sub_title', 'content'], request.json):
        return Response.client_error("no ['title', 'sub_title', 'content'] in request")

    news = News(
        title=request.json['title'],
        sub_title=request.json['sub_title'],
        content=request.json['content']
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

    if 'title' in request.json:
        news.title = request.json['title']
    if 'sub_title' in request.json:
        news.sub_title = request.json['sub_title']
    if 'content' in request.json:
        news.content = request.json['content']

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
