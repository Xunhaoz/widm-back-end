import os
from uuid import uuid4
from pathlib import Path
from datetime import datetime
from models.member_model import db, Member
from models.responses import Response
from utiles.api_helper import api_input_get, api_input_check

from flask import Blueprint, request, send_file

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
            name:
              example: '張嘉惠'
              type: string
            name_en:
              example: 'Chang, Chia-Hui.'
              type: string
            position:
              example: 'PHD'
              type: string
            intro:
              example: '歡迎大家到 WIDM 實驗室'
              type: string
            graduate_year:
              example: '2024-01'
              type: string
    responses:
      200:
        description: post paper successfully
        schema:
          id: member
          properties:
            description:
              example: 'post member successfully'
              type: string
            response:
              properties:
                id:
                  example: '1'
                  type: integer
                name:
                  example: '張嘉惠'
                  type: string
                name_en:
                  example: 'Chang, Chia-Hui.'
                  type: string
                position:
                  example: 'PHD'
                  type: string
                intro:
                  example: '歡迎大家到 WIDM 實驗室'
                  type: string
                image_existed:
                  example: true
                  type: boolean
                graduate_year:
                  example: '2024-01'
                  type: string
                update_time:
                  example: 'Tue, 06 Aug 2024 10:39:27 GMT'
                  type: string
                create_time:
                  example: 'Tue, 06 Aug 2024 10:39:27 GMT'
                  type: string
      400:
        description: no ['member_name', 'member_intro'] or content in form
    """
    if not api_input_check(['name', 'name_en', 'position', 'intro', 'graduate_year'], request.json):
        return Response.client_error("no ['name', 'name_en', 'position', 'intro', 'graduate_year'] or content in json")

    name, name_en, position, intro, graduate_year = api_input_get(
        ['name', 'name_en', 'position', 'intro', 'graduate_year'], request.json)
    graduate_year = datetime.strptime(graduate_year, '%Y-%m') if graduate_year else None

    member = Member(
        name=name,
        name_en=name_en,
        position=position,
        intro=intro,
        graduate_year=graduate_year
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
                    example: '1'
                    type: integer
                  name:
                    example: '張嘉惠'
                    type: string
                  name_en:
                    example: 'Chang, Chia-Hui.'
                    type: string
                  position:
                    example: 'PHD'
                    type: string
                  intro:
                    example: '歡迎大家到 WIDM 實驗室'
                    type: string
                  graduate_year:
                    example: '2024-01'
                    type: string
                  image_existed:
                    example: true
                    type: boolean
                  update_time:
                    example: 'Tue, 06 Aug 2024 10:39:27 GMT'
                    type: string
                  create_time:
                    example: 'Tue, 06 Aug 2024 10:39:27 GMT'
                    type: string
      404:
        description: no member exist
    """
    return Response.response('get members successfully', [m.to_dict() for m in Member.query.all()])


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
      404:
        description: member_id not exist
    """
    member = Member.query.get(member_id)
    if not member:
        return Response.not_found('member not exist')

    if member.image_path:
        os.remove(member.image_path)

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
    responses:
      200:
        description: patch member successfully
        schema:
          id: member
      404:
        description: member_id not exist
    """
    member = Member.query.get(member_id)
    if not member:
        return Response.not_found('member not exist')

    if 'name' in request.json:
        member.name = request.json['name']
    if 'name_en' in request.json:
        member.name_en = request.json['name_en']
    if 'position' in request.json:
        member.position = request.json['position']
    if 'intro' in request.json:
        member.intro = request.json['intro']
    if 'graduate_year' in request.json:
        member.graduate_year = datetime.strptime(request.json['graduate_year'], '%Y-%m') \
            if request.json['graduate_year'] else None

    db.session.commit()
    return Response.response('patch member successfully', member.to_dict())


@member_blueprint.route('<member_id>/member-image', methods=['POST'])
def post_member_image(member_id):
    """
    post member image
    ---
    tags:
      - member
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
          id: member
      400:
        description: no ['image'] or content in form
      404:
        description: member_id not exist
    """
    if not api_input_check(['image'], request.files):
        return Response.client_error("no ['image'] or content in form")

    member = Member.query.get(member_id)
    if not member:
        return Response.not_found('member not exist')

    if member.image_path:
        os.remove(member.image_path)

    image = request.files['image']
    image_uuid = uuid4().hex
    image_name = image.filename
    image_path = f'./statics/images/{image_uuid}.{image_name.split(".")[-1]}'
    image.save(image_path)

    member.image_path = str(image_path)
    db.session.commit()
    return Response.response('post member image successfully', member.to_dict())


@member_blueprint.route('<member_id>/member-image', methods=['GET'])
def get_member_image(member_id):
    """
    get member images
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
        description: get paper attachment successfully
      404:
        description: paper_id or paper_attachment_id not exist
    """
    member = Member.query.get(member_id)
    if not Member.query.get(member_id):
        return Response.not_found('member not exist')

    if not member.image_path:
        return Response.not_found('image not exist')

    return send_file(member.image_path)
