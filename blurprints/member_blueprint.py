import os
from uuid import uuid4

from models.member_model import db, Member, MemberImage
from models.responses import Response
from utiles.api_helper import api_input_get, api_input_check

from flask import Blueprint, request, send_file
from sqlalchemy.orm import joinedload

member_blueprint = Blueprint('member', __name__)


@member_blueprint.route('', methods=['POST'])
def post_member():
    """
    post member
    ---
    tags:
      - member
    parameters:
      - in: body
        name: member
        schema:
          id: member_input
          properties:
            member_name:
              type: string
            member_intro:
              type: string
            member_character:
              type: string
    responses:
      200:
        description: post paper successfully
        schema:
          id: member
          properties:
            description:
              type: string
            response:
              properties:
                member_name:
                  type: string
                member_intro:
                  type: string
                create_time:
                  type: string
                update_time:
                  type: string
      400:
        description: no ['member_name', 'member_intro'] or content in form
    """
    if not api_input_check(['member_name', 'member_intro', 'member_character'], request.json):
        return Response.client_error("no ['member_name', 'member_intro', 'member_character'] or content in json")

    member_name, member_intro, member_character = api_input_get(['member_name', 'member_intro', 'member_character'],
                                                                request.json)

    member = Member(
        member_name=member_name,
        member_intro=member_intro,
        member_character=member_character
    )

    db.session.add(member)
    db.session.commit()
    return Response.response('post member successfully', member.to_dict())


@member_blueprint.route('', methods=['GET'])
def get_members():
    """
    get members
    ---
    tags:
      - member
    responses:
      200:
        description: get members successfully
        schema:
          id: members
          properties:
            description:
              type: string
            response:
              type: array
              items:
                properties:
                  id:
                    type: integer
                  member_name:
                    type: string
                  member_intro:
                    type: string
                  member_image:
                    type: string
                  create_time:
                    type: string
                  update_time:
                    type: string
      404:
        description: no member exist
    """

    members = (
        Member.query
        .options(joinedload(Member.member_image))
    ).all()

    members_payload = []
    for member in members:
        member_payload = member.to_dict()
        member_payload['member_image'] = member.member_image.image_uuid \
            if member.member_image else None
        members_payload.append(member_payload)

    return Response.response('get members successfully', members_payload)


@member_blueprint.route('<member_id>', methods=['DELETE'])
def delete_member(member_id):
    """
    delete member
    ---
    tags:
      - member
    parameters:
      - in: path
        name: member_id
        type: integer
        required: true
    responses:
      200:
        description: delete member successfully
        schema:
          id: member
          properties:
            description:
              type: string
            response:
              properties:
                member_name:
                  type: string
                member_intro:
                  type: string
                create_time:
                  type: string
                update_time:
                  type: string
      404:
        description: member_id not exist
    """
    member = Member.query.get(member_id)
    if not member:
        return Response.not_found('member not exist')

    member_image = MemberImage.query.filter_by(member_id=member_id).first()
    if member_image:
        os.remove(member_image.image_path)

    db.session.delete(member)
    db.session.commit()
    return Response.response('delete member successfully', member.to_dict())


@member_blueprint.route('<member_id>', methods=['PATCH'])
def patch_member(member_id):
    """
    patch member
    ---
    tags:
      - member
    parameters:
      - in: path
        name: member_id
        type: integer
        required: true
      - in: body
        name: member
        schema:
          id: member_input
          properties:
            member_name:
              type: string
            member_intro:
              type: string
            member_character:
              type: string
    responses:
      200:
        description: patch member successfully
        schema:
          id: member
          properties:
            description:
              type: string
            response:
              properties:
                member_name:
                  type: string
                member_intro:
                  type: string
                create_time:
                  type: string
                update_time:
                  type: string
      400:
        description: no ['member_name', 'member_intro'] or content in form
      404:
        description: member_id not exist
    """
    member = Member.query.get(member_id)
    if not member:
        return Response.not_found('member not exist')
    if 'member_name' in request.json:
        member.member_name = request.json['member_name']
    if 'member_intro' in request.json:
        member.member_intro = request.json['member_intro']
    if 'member_character' in request.json:
        member.member_character = request.json['member_character']
    db.session.commit()
    return Response.response('patch member successfully', member.to_dict())


@member_blueprint.route('<member_id>/member-image', methods=['POST'])
def post_member_image(member_id):
    """
    post member image
    ---
    tags:
      - member_image
    parameters:
      - in: path
        name: member_id
        type: integer
        required: true
      - in: formData
        name: image
        type: file
        required: true
    responses:
      200:
        description: post member image successfully
        schema:
          id: member_image
          properties:
            description:
              type: string
            response:
              properties:
                id:
                  type: integer
                member_id:
                  type: integer
                image_uuid:
                  type: string
                create_time:
                  type: string
                update_time:
                  type: string
      400:
        description: no ['image'] or content in form
      404:
        description: member_id not exist
    """
    if not api_input_check(['image'], request.files):
        return Response.client_error("no ['image'] or content in form")

    if not Member.query.get(member_id):
        return Response.not_found('member not exist')

    if MemberImage.query.filter_by(member_id=member_id).first():
        return Response.client_error("only one image is allowed")

    image = request.files['image']
    image_uuid = uuid4().hex
    image_name = image.filename
    image_path = f'./statics/images/{image_uuid}.{image_name.split(".")[-1]}'
    image.save(image_path)

    member_image = MemberImage(
        member_id=member_id,
        image_uuid=image_uuid,
        image_name=image_name,
        image_path=image_path
    )

    db.session.add(member_image)
    db.session.commit()
    return Response.response('post member image successfully', member_image.to_dict())


@member_blueprint.route('<member_id>/member-image/<member_image_uuid>', methods=['GET'])
def get_member_image(member_id, member_image_uuid):
    """
    get member images
    ---
    tags:
      - member_image
    parameters:
      - in: path
        name: member_id
        type: integer
        required: true
      - in: path
        name: member_image_uuid
        type: string
        required: true
    responses:
      200:
        description: get paper attachment successfully
      404:
        description: paper_id or paper_attachment_id not exist
    """
    if not Member.query.get(member_id):
        return Response.not_found('member not exist')

    member_image = MemberImage.query.filter_by(member_id=member_id, image_uuid=member_image_uuid).first()
    if not member_image:
        return Response.not_found('image not exist')

    return send_file(member_image.image_path)


@member_blueprint.route('<member_id>/member-image/<member_image_uuid>', methods=['DELETE'])
def delete_member_image(member_id, member_image_uuid):
    """
    delete member image
    ---
    tags:
      - member_image
    parameters:
      - in: path
        name: member_id
        type: integer
        required: true
      - in: path
        name: member_image_uuid
        type: string
        required: true
    responses:
      200:
        description: delete attachment successfully
        schema:
          id: paper_attachment
          properties:
            description:
              type: string
            response:
              properties:
                id:
                  type: integer
                member_id:
                  type: integer
                image_uuid:
                  type: string
                create_time:
                  type: string
                update_time:
                  type: string
      404:
        description: member_id or member_image_uuid not exist
    """
    if not Member.query.get(member_id):
        return Response.not_found('member not exist')

    member_image = MemberImage.query.filter_by(image_uuid=member_image_uuid).first()
    if not member_image:
        return Response.not_found('attachment not exist')

    os.remove(member_image.image_path)
    db.session.delete(member_image)
    db.session.commit()

    return Response.response('delete member image successfully', member_image.to_dict())
