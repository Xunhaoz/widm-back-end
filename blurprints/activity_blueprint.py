import os
from uuid import uuid4

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
        required:
          - activity_title
          - activity_sub_title
        properties:
          activity_title:
            type: string
          activity_sub_title:
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
                  type: integer
                activity_title:
                  type: string
                activity_sub_title:
                  type: string
                create_time:
                  type: string
                update_time:
                  type: string
      400:
        description: no ['activity_title', 'activity_sub_title'] or content in form
    """
    if not api_input_check(['activity_title', 'activity_sub_title'], request.json):
        return Response.client_error("no ['activity_title', 'activity_sub_title'] in form")

    activity_title, activity_sub_title = api_input_get(['activity_title', 'activity_sub_title'], request.json)
    activity = Activity(
        activity_title=activity_title,
        activity_sub_title=activity_sub_title
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
                    type: integer
                  activity_title:
                    type: string
                  activity_sub_title:
                    type: string
                  activity_image:
                    type: array
                    items:
                      type: string
                  create_time:
                    type: string
                  update_time:
                    type: string
                  activity_image:
                    type: array
                    items:
                      type: string
      404:
        description: activity not exist
    """
    activities = (
        Activity.query
        .options(joinedload(Activity.activity_image))
    ).all()

    activities_payload = []
    for activity in activities:
        activity_payload = activity.to_dict()
        activity_payload['activity_image'] = [
            activity_image.image_uuid for activity_image in activity.activity_image
        ] or None
        activities_payload.append(activity_payload)

    return Response.response(
        'get activities successfully',
        activities_payload
    )


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
          required:
            - activity_title
            - activity_sub_title
          properties:
            activity_title:
              type: string
            activity_sub_title:
              type: string
    responses:
      200:
        description: patch activity successfully
        schema:
          id: activity
          properties:
            description:
              type: string
            response:
              properties:
                id:
                  type: integer
                activity_title:
                  type: string
                activity_sub_title:
                  type: string
                create_time:
                  type: string
                update_time:
                  type: string
      400:
        description: no ['activity_title', 'activity_sub_title'] or content in form
      404:
        description: activity not exist
    """
    activity = Activity.query.get(activity_id)
    if not activity:
        return Response.not_found('activity not exist')

    if 'activity_title' in request.json:
        activity.activity_title = request.json['activity_title']

    if 'activity_sub_title' in request.json:
        activity.activity_sub_title = request.json['activity_sub_title']

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
          properties:
            description:
              type: string
            response:
              properties:
                id:
                  type: integer
                activity_title:
                  type: string
                activity_sub_title:
                  type: string
                create_time:
                  type: string
                update_time:
                  type: string
      404:
        description: activity not exist
    """
    if not Activity.query.get(activity_id):
        return Response.not_found('activity not exist')

    activity = Activity.query.get(activity_id)
    for activity_image in activity.activity_image:
        os.remove(activity_image.image_path)

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
          id: activity_image
          properties:
            description:
              type: string
            response:
              properties:
                activity_id:
                  type: integer
                image_uuid:
                  type: string
                image_name:
                  type: string
                create_time:
                  type: string
                update_time:
                  type: string
      400:
        description: no ['image'] or content in form
      404:
        description: activity not exist
    """
    if not api_input_check(['image'], request.files):
        return Response.client_error("no ['image'] or content in form")

    if not Activity.query.get(activity_id):
        return Response.not_found('activity not exist')

    image = request.files['image']
    image_uuid = uuid4().hex
    image_name = image.filename
    image_path = f'./statics/images/{image_uuid}.{image_name.split(".")[-1]}'
    image.save(image_path)

    activity_image = ActivityImage(
        activity_id=activity_id,
        image_uuid=image_uuid,
        image_name=image_name,
        image_path=image_path,
    )
    db.session.add(activity_image)
    db.session.commit()
    return Response.response('post activity image successfully', activity_image.to_dict())


@activity_blueprint.route('<activity_id>/activity-image/<activity_image_uuid>', methods=['GET'])
def get_activity_image(activity_id, activity_image_uuid):
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
        name: activity_image_uuid
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

    activity_image = ActivityImage.query.filter_by(activity_id=activity_id, image_uuid=activity_image_uuid).first()
    if not activity_image:
        return Response.not_found('activity image not exist')

    return send_file(activity_image.image_path)


@activity_blueprint.route('<activity_id>/activity-image/<activity_image_uuid>', methods=['DELETE'])
def delete_activity_image(activity_id, activity_image_uuid):
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
        name: activity_image_uuid
        type: string
        required: true
    responses:
      200:
        description: delete activity image successfully
        schema:
          id: activity_image
          properties:
            description:
              type: string
            response:
              properties:
                activity_id:
                  type: integer
                image_uuid:
                  type: string
                image_name:
                  type: string
                create_time:
                  type: string
                update_time:
                  type: string
      404:
        description: activity not exist or activity image not exist
    """
    if not Activity.query.get(activity_id):
        return Response.not_found('activity not exist')

    activity_image = ActivityImage.query.filter_by(activity_id=activity_id, image_uuid=activity_image_uuid).first()
    if not activity_image:
        return Response.not_found('activity image not exist')

    os.remove(activity_image.image_path)
    db.session.delete(activity_image)
    db.session.commit()
    return Response.response('delete activity image successfully', activity_image.to_dict())
