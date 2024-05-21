import os
import json
from uuid import uuid4

from models.paper_model import db, Paper, PaperAttachment
from models.responses import Response
from utiles.api_helper import api_input_get, api_input_check

from flask import Blueprint, request, send_file
from sqlalchemy.orm import joinedload

paper_blueprint = Blueprint('paper', __name__)


@paper_blueprint.route('', methods=['POST'])
def post_paper():
    """
    post paper
    ---
    tags:
      - paper
    parameters:
    - in: body
      name: paper
      schema:
        properties:
          paper_publish_year:
            type: integer
          paper_title:
            type: string
          paper_origin:
            type: string
          paper_link:
            required: false
            type: string
          paper_authors:
            required: false
            type: array
            items:
              type: string
          paper_tags:
            required: false
            type: array
            items:
              type: string
    responses:
      200:
        description: post paper successfully
        schema:
          id: paper
          type: object
          properties:
            description:
              type: string
            response:
              type: object
              properties:
                paper_id:
                  type: integer
                paper_publish_year:
                  type: integer
                paper_title:
                  type: string
                paper_origin:
                  type: string
                paper_link:
                  type: string
                paper_authors:
                  type: array
                  items:
                    type: string
                paper_tags:
                  type: array
                  items:
                    type: string
                update_time:
                  type: string
                create_time:
                  type: string
      400:
        description: no ['paper_publish_year', 'paper_title', 'paper_origin', 'paper_attachment', 'paper_link'] or content in form
    """
    if not api_input_check(
            ['paper_publish_year', 'paper_title', 'paper_origin'], request.json
    ):
        return Response.client_error(
            "no ['paper_publish_year', 'paper_title', 'paper_origin', 'paper_attachment', 'paper_link'] or content in form"
        )

    paper_publish_year, paper_title, paper_origin = api_input_get(
        ['paper_publish_year', 'paper_title', 'paper_origin'], request.json
    )
    paper = Paper(
        paper_publish_year=paper_publish_year,
        paper_title=paper_title,
        paper_origin=paper_origin,
        paper_link=request.json.get('project_description', None),
        paper_tags=json.dumps(request.json['paper_tags']) if 'paper_tags' in request.json else None,
        paper_authors=json.dumps(request.json['paper_authors']) if 'paper_authors' in request.json else None,
    )
    db.session.add(paper)
    db.session.commit()
    return Response.response('post paper successfully', paper.to_dict())


@paper_blueprint.route('', methods=['GET'])
def get_papers():
    """
    get_papers
    ---
    tags:
      - paper
    responses:
      200:
        description: get papers successfully
        schema:
          id: paper
    """
    papers = (
        Paper.query
        .options(joinedload(Paper.paper_attachment))
        .order_by(Paper.paper_publish_year.desc())
    ).all()

    papers_payload = []
    for paper in papers:
        paper_payload = paper.to_dict()

        if paper_payload['paper_tags']:
            paper_payload['paper_tags'] = json.loads(paper_payload['paper_tags'])

        if paper_payload['paper_authors']:
            paper_payload['paper_authors'] = json.loads(paper_payload['paper_authors'])

        paper_payload['paper_attachment'] = paper.paper_attachment.attachment_uuid \
            if paper.paper_attachment else None

        papers_payload.append(paper_payload)

    return Response.response("get papers successfully", papers_payload)


@paper_blueprint.route('<paper_id>', methods=['PATCH'])
def patch_paper(paper_id):
    """
    patch paper
    ---
    tags:
      - paper
    parameters:
    - in: path
      name: paper_id
      type: integer
      required: true
    - in: body
      name: paper
      schema:
        properties:
          paper_publish_year:
            type: integer
          paper_title:
            type: string
          paper_origin:
            type: string
          paper_link:
            required: false
            type: string
          paper_authors:
            required: false
            type: array
            items:
              type: string
          paper_tags:
            required: false
            type: array
            items:
              type: string
    responses:
      200:
        description: update paper successfully
        schema:
          id: paper
      404:
        description: paper_id not exist
    """
    paper = Paper.query.get(paper_id)
    if not paper:
        return Response.not_found('paper not exist')

    if 'paper_publish_year' in request.json:
        paper.paper_publish_year = request.json['paper_publish_year']
    if 'paper_title' in request.json:
        paper.paper_title = request.json['paper_title']
    if 'paper_origin' in request.json:
        paper.paper_origin = request.json['paper_origin']
    if 'paper_link' in request.json:
        paper.paper_link = request.json['paper_link']
    if 'paper_tags' in request.json:
        paper.paper_link = json.dumps(request.json['paper_tags'])
    if 'paper_authors' in request.json:
        paper.paper_link = json.dumps(request.json['paper_authors'])

    db.session.commit()
    return Response.response('update paper successfully', paper.to_dict())


@paper_blueprint.route('<paper_id>', methods=['DELETE'])
def delete_paper(paper_id):
    """
    delete paper
    ---
    tags:
      - paper
    parameters:
      - in: path
        name: paper_id
        type: integer
        required: true
    responses:
      200:
        description: delete paper successfully
        schema:
          id: paper
          properties:
            description:
              type: string
            response:
              properties:
                paper_publish_year:
                  type: integer
                paper_title:
                  type: string
                paper_origin:
                  type: string
                paper_link:
                  type: string
                create_time:
                  type: string
                update_time:
                  type: string
      404:
        description: paper_id not exist
    """
    paper = Paper.query.get(paper_id)
    if not paper:
        return Response.not_found('paper not exist')

    paper_attachment = PaperAttachment.query.filter_by(paper_id=paper_id).first()
    if paper_attachment:
        os.remove(f'./statics/attachments/{paper_attachment.attachment_uuid}')

    db.session.delete(paper)
    db.session.commit()
    return Response.response('delete paper successfully', paper.to_dict())


@paper_blueprint.route('<paper_id>/paper-attachment', methods=['POST'])
def post_paper_attachment(paper_id):
    """
    post paper attachment
    ---
    tags:
      - paper_attachment
    parameters:
      - in: path
        name: paper_id
        type: integer
        required: true
      - in: formData
        name: paper_attachment
        type: file
        required: true
    responses:
      200:
        description: post paper attachment successfully
        schema:
          id: paper_attachment
          type: object
          properties:
            description:
              type: string
            response:
              type: object
              properties:
                attachment_id:
                  type: integer
                paper_id:
                  type: integer
                paper_path:
                  type: integer
                attachment_name:
                  type: integer
                attachment_uuid:
                  type: string
                create_time:
                  type: string
                update_time:
                  type: string
      400:
        description: no ['paper_attachment'] or content in form
      404:
        description: paper_id not exist
    """
    if not api_input_check(['paper_attachment'], request.files):
        return Response.client_error("no ['paper_attachment'] or content in form")

    if not Paper.query.get(paper_id):
        return Response.not_found('paper not exist')

    if PaperAttachment.query.filter_by(paper_id=paper_id).first():
        return Response.client_error("only one attachment is allowed")

    attachment = request.files['paper_attachment']
    attachment_uuid = uuid4().hex
    attachment_name = attachment.filename
    attachment_path = f'./statics/attachments/{attachment_uuid}.{attachment_name.split(".")[-1]}'
    attachment.save(attachment_path)
    paper_attachment = PaperAttachment(
        paper_id=paper_id,
        attachment_uuid=attachment_uuid,
        attachment_name=attachment_name,
        attachment_path=attachment_path
    )

    db.session.add(paper_attachment)
    db.session.commit()
    return Response.response('post paper attachment successfully', paper_attachment.to_dict())


@paper_blueprint.route('<paper_id>/paper-attachment/<paper_attachment_uuid>', methods=['GET'])
def get_paper_attachment(paper_id, paper_attachment_uuid):
    """
    get paper attachment
    ---
    tags:
      - paper_attachment
    parameters:
      - in: path
        name: paper_id
        type: integer
        required: true
      - in: path
        name: paper_attachment_uuid
        type: string
        required: true
    responses:
      200:
        description: get paper attachment successfully
      404:
        description: paper_id or paper_attachment_id not exist
    """
    if not Paper.query.get(paper_id):
        return Response.not_found('paper not exist')

    paper_attachment = PaperAttachment.query.filter_by(paper_id=paper_id, attachment_uuid=paper_attachment_uuid).first()
    if not paper_attachment:
        return Response.not_found('attachment not exist')

    return send_file(
        paper_attachment.attachment_path,
        as_attachment=True,
        download_name=paper_attachment.attachment_name
    )


@paper_blueprint.route('<paper_id>/paper-attachment/<paper_attachment_uuid>', methods=['DELETE'])
def delete_paper_attachment(paper_id, paper_attachment_uuid):
    """
    delete paper attachment
    ---
    tags:
      - paper_attachment
    parameters:
      - in: path
        name: paper_id
        type: integer
        required: true
      - in: path
        name: paper_attachment_uuid
        type: string
        required: true
    responses:
      200:
        description: delete attachment successfully
        schema:
          id: paper_attachment
      404:
        description: paper_id or paper_attachment_id not exist
    """
    if not Paper.query.get(paper_id):
        return Response.not_found('paper not exist')

    paper_attachment = PaperAttachment.query.filter_by(paper_id=paper_id, attachment_uuid=paper_attachment_uuid).first()
    if not paper_attachment:
        return Response.not_found('attachment not exist')

    os.remove(paper_attachment.attachment_path)
    db.session.delete(paper_attachment)
    db.session.commit()

    return Response.response('delete attachment successfully', paper_attachment.to_dict())
