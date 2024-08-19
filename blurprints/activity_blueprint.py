import os
from uuid import uuid4
from pathlib import Path
from datetime import datetime

from models.activity_model import db, Activity, ActivityImage
from models.responses import Response
from utiles.api_helper import api_input_get, api_input_check

from flask import Blueprint, request, send_file
from sqlalchemy.orm import joinedload

activity_blueprint = Blueprint('activity', __name__)


@activity_blueprint.route('', methods=['POST'])
def post_activity():
    """
    post activity
    ---
    tags:
      - activity
    parameters:
      - in: body
        name: activity
        schema:
          id: activity_input
          properties:
            title:
              example: title
              type: string
            sub_title:
              example: sub_title
              type: string
            date:
              example: '2024-01-01'
              type: string
    responses:
      200:
        description: post activity successfully
        schema:
          id: activity
          properties:
            description:
              type: string
            response:
              properties:
                id:
                  example: 1
                  type: integer
                title:
                  example: title
                  type: string
                sub_title:
                  example: sub_title
                  type: string
                images:
                  example: [1,2,3]
                  type: array
                create_time:
                  example: 'Tue, 06 Aug 2024 10:39:27 GMT'
                  type: string
                update_time:
                  example: 'Tue, 06 Aug 2024 10:39:27 GMT'
                  type: string
      400:
        description: no ['activity_title', 'activity_sub_title'] or content in form
    """
    if not api_input_check(['title', 'sub_title', 'date'], request.json):
        return Response.client_error("no ['title', 'sub_title', 'date'] in form")

    title, sub_title, date = api_input_get(['title', 'sub_title', 'date'], request.json)
    date = datetime.strptime(date, '%Y-%m-%d')
    activity = Activity(
        title=title,
        sub_title=sub_title,
        date=date
    )
    db.session.add(activity)
    db.session.commit()
    return Response.response('post activity successfully', activity.to_dict())


@activity_blueprint.route('', methods=['GET'])
def get_activities():
    """
    get activity
    ---
    tags:
      - activity
    responses:
      200:
        description: get activities successfully
        schema:
          id: activities
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
                    example: title
                    type: string
                  sub_title:
                    example: sub_title
                    type: string
                  images:
                    example: [1,2,3]
                    type: array
                  date:
                    example: '2024-01-01'
                    type: string
                  create_time:
                    example: 'Tue, 06 Aug 2024 10:39:27 GMT'
                    type: string
                  update_time:
                    example: 'Tue, 06 Aug 2024 10:39:27 GMT'
                    type: string
      404:
        description: activity not exist
    """
    activities = Activity.query.all()
    return Response.response('get activities successfully', [activity.to_dict() for activity in activities])


@activity_blueprint.route('<activity_id>', methods=['PATCH'])
def patch_activity(activity_id):
    """
    patch activity
    ---
    tags:
      - activity
    parameters:
      - in: path
        name: activity_id
        type: integer
        required: true
      - in: body
        name: activity
        schema:
          id: activity_input
    responses:
      200:
        description: patch activity successfully
        schema:
          id: activity
      404:
        description: activity not exist
    """
    activity = Activity.query.get(activity_id)
    if not activity:
        return Response.not_found('activity not exist')

    if 'title' in request.json:
        activity.title = request.json['title']

    if 'sub_title' in request.json:
        activity.sub_title = request.json['sub_title']

    if 'date' in request.json and request.json['date']:
        activity.date = datetime.strptime(request.json['date'], '%Y-%m-%d')

    db.session.commit()
    return Response.response('patch activity successfully', activity.to_dict())


@activity_blueprint.route('<activity_id>', methods=['DELETE'])
def delete_activity(activity_id):
    """
    delete activity
    ---
    tags:
      - activity
    parameters:
      - in: path
        name: activity_id
        type: integer
        required: true
    responses:
      200:
        description: delete activity successfully
        schema:
          id: activity
      404:
        description: activity not exist
    """
    activity = Activity.query.get(activity_id)
    if not activity:
        return Response.not_found('activity not exist')

    activity_images = ActivityImage.query.filter_by(activity_id=activity_id).all()
    for activity_image in activity_images:
        os.remove(activity_image.image_path)
        db.session.delete(activity_image)

    db.session.delete(activity)
    db.session.commit()
    return Response.response('delete activity successfully', activity.to_dict())


@activity_blueprint.route('<activity_id>/activity-image', methods=['POST'])
def post_activity_image(activity_id):
    """
    post activity image
    ---
    tags:
      - activity_image
    parameters:
      - in: path
        name: activity_id
        type: integer
        required: true
      - in: formData
        name: image
        type: file
        required: true
    responses:
      200:
        description: post activity image successfully
        schema:
          id: activity
      400:
        description: no ['image'] or content in form
      404:
        description: activity not exist
    """
    if not api_input_check(['image'], request.files):
        return Response.client_error("no ['image'] or content in form")

    activity = Activity.query.get(activity_id)
    if not activity:
        return Response.not_found('activity not exist')

    image = request.files['image']
    image_uuid = uuid4().hex
    image_name = image.filename
    image_path = f'./statics/images/{image_uuid}.{image_name.split(".")[-1]}'
    image.save(image_path)

    activity_image = ActivityImage(
        activity_id=activity_id,
        image_path=str(image_path)
    )
    db.session.add(activity_image)
    db.session.commit()
    return Response.response('post activity image successfully', activity.to_dict())


@activity_blueprint.route('<activity_id>/activity-image/<image_id>', methods=['GET'])
def get_activity_image(activity_id, image_id):
    """
    get activity image
    ---
    tags:
      - activity_image
    parameters:
      - in: path
        name: activity_id
        type: integer
        required: true
      - in: path
        name: image_id
        type: string
        required: true
    responses:
      200:
        description: get activity image successfully
      404:
        description: activity not exist or activity image not exist
    """
    if not Activity.query.get(activity_id):
        return Response.not_found('activity not exist')

    activity_image = ActivityImage.query.get(image_id)
    if not activity_image:
        return Response.not_found('activity image not exist')

    return send_file(activity_image.image_path)


@activity_blueprint.route('<activity_id>/activity-image/<image_id>', methods=['DELETE'])
def delete_activity_image(activity_id, image_id):
    """
    delete activity image
    ---
    tags:
      - activity_image
    parameters:
      - in: path
        name: activity_id
        type: integer
        required: true
      - in: path
        name: image_id
        type: string
        required: true
    responses:
      200:
        description: delete activity image successfully
        schema:
          id: activity
      404:
        description: activity not exist or activity image not exist
    """
    activity = Activity.query.get(activity_id)
    if not activity:
        return Response.not_found('activity not exist')

    activity_image = ActivityImage.query.get(image_id)
    if not activity_image:
        return Response.not_found('activity image not exist')

    os.remove(activity_image.image_path)
    db.session.delete(activity_image)
    db.session.commit()
    return Response.response('delete activity image successfully', activity.to_dict())
