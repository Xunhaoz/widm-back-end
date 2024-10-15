import os
from json import dumps, loads
from uuid import uuid4
from pathlib import Path
from datetime import datetime

from models.paper_model import db, Paper
from models.responses import Response
from utiles.api_helper import api_input_get, api_input_check

from flask import Blueprint, request, send_file
from sqlalchemy import desc, or_

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
          id: paper_input
          properties:
            title:
              example: "title"
              type: string
            sub_title:
              example: "sub_title"
              type: string
            authors:
              example: ["author1", "author2"]
              type: array
            tags:
              example: ["tag1", "tag2"]
              type: array
            publish_year:
              example: '2021-01'
              type: string
            origin:
              example: Space Weather
              type: string
            link:
              example: "https://www.spaceweather.com"
              type: string
            type:
              example: ["type1", "type2"]
              type: array
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
                id:
                  example: 1
                  type: integer
                title:
                  example: "title"
                  type: string
                sub_title:
                  example: "sub_title"
                  type: string
                authors:
                  example: ["author1", "author2"]
                  type: array
                tags:
                  example: ["tag1", "tag2"]
                  type: array
                publish_year:
                  example: '2021-01'
                  type: string
                origin:
                  example: Space Weather
                  type: string
                link:
                  example: "https://www.spaceweather.com"
                  type: string
                type:
                  example: ["type1", "type2"]
                  type: array
                attachment_existed:
                  example: false
                  type: boolean
                create_time:
                  example: 'Tue, 06 Aug 2024 10:39:27 GMT'
                  type: string
                update_time:
                  example: 'Tue, 06 Aug 2024 10:39:27 GMT'
                  type: string
      400:
        description: no ['paper_publish_year', 'paper_title', 'paper_origin', 'paper_attachment', 'paper_link'] or content in form
    """
    if not api_input_check(
            ['title', 'sub_title', 'authors', 'tags', 'publish_year', 'origin', 'link', 'type'], request.json
    ):
        return Response.client_error(
            "no ['title', 'sub_title', 'authors', 'tags', 'publish_year', 'origin', 'link', 'types'] or content in form"
        )

    title, sub_title, authors, tags, publish_year, origin, link, types = api_input_get(
        ['title', 'sub_title', 'authors', 'tags', 'publish_year', 'origin', 'link', 'types'], request.json
    )


    try:
        publish_year = datetime.strptime(publish_year, '%Y-%m')
    except ValueError:
        return Response.client_error('publish_year format error')

    authors = dumps(authors)
    tags = dumps(tags)
    types = dumps(types)

    paper = Paper(
        title=title,
        sub_title=sub_title,
        authors=authors,
        tags=tags,
        publish_year=publish_year,
        origin=origin,
        link=link,
        types=types,
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
          id: papers
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
                    example: "title"
                    type: string
                  sub_title:
                    example: "sub_title"
                    type: string
                  authors:
                    example: ["author1", "author2"]
                    type: array
                  tags:
                    example: ["tag1", "tag2"]
                    type: array
                  publish_year:
                    example: '2021-01'
                    type: string
                  origin:
                    example: Space Weather
                    type: string
                  link:
                    example: "https://www.spaceweather.com"
                    type: string
                  types:
                    example: ["type1", "type2"]
                    type: array
                  attachment_existed:
                    example: false
                    type: boolean
                  create_time:
                    example: 'Tue, 06 Aug 2024 10:39:27 GMT'
                    type: string
                  update_time:
                    example: 'Tue, 06 Aug 2024 10:39:27 GMT'
                    type: string
    """
    papers = db.session.query(Paper)
    papers = papers.order_by(desc(Paper.create_time)).all()
    return Response.response("get papers successfully", [paper.to_dict() for paper in papers])


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
        id: paper_input
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

    if 'title' in request.json:
        paper.title = request.json['title']
    if 'sub_title' in request.json:
        paper.sub_title = request.json['sub_title']
    if 'authors' in request.json:
        paper.authors = dumps(request.json['authors'])
    if 'tags' in request.json:
        paper.tags = dumps(request.json['tags'])
    if 'publish_year' in request.json and request.json['publish_year']:
        try:
            paper.publish_year = datetime.strptime(request.json['publish_year'], '%Y-%m')
        except ValueError:
            return Response.client_error('publish_year format error')
    if 'origin' in request.json:
        paper.origin = request.json['origin']
    if 'link' in request.json:
        paper.link = request.json['link']
    if 'types' in request.json:
        paper.types = dumps(request.json['types'])

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
      404:
        description: paper_id not exist
    """
    paper = Paper.query.get(paper_id)
    if not paper:
        return Response.not_found('paper not exist')

    if paper.attachment_path:
        os.remove(paper.attachment_path)

    db.session.delete(paper)
    db.session.commit()
    return Response.response('delete paper successfully', paper.to_dict())


@paper_blueprint.route('<paper_id>/paper-attachment', methods=['POST'])
def post_paper_attachment(paper_id):
    """
    post paper attachment
    ---
    tags:
      - paper
    parameters:
      - in: path
        name: paper_id
        type: integer
        required: true
      - in: formData
        name: attachment
        type: file
        required: true
    responses:
      200:
        description: post paper attachment successfully
        schema:
          id: paper
      400:
        description: no ['paper_attachment'] or content in form
      404:
        description: paper_id not exist
    """
    if not api_input_check(['attachment'], request.files):
        return Response.client_error("no ['attachment'] or content in form")

    paper = Paper.query.get(paper_id)
    if not paper:
        return Response.not_found('paper not exist')

    if paper.attachment_path:
        os.remove(paper.attachment_path)

    attachment = request.files['attachment']
    attachment_uuid = uuid4().hex
    attachment_name = attachment.filename
    attachment_path = f'./statics/attachments/{attachment_uuid}.{attachment_name.split(".")[-1]}'
    attachment.save(attachment_path)
    paper.attachment_path = attachment_path
    db.session.commit()
    return Response.response('post paper attachment successfully', paper.to_dict())


@paper_blueprint.route('<paper_id>/paper-attachment', methods=['GET'])
def get_paper_attachment(paper_id):
    """
    get paper attachment
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
        description: get paper attachment successfully
      404:
        description: paper_id or paper_attachment_id not exist
    """
    paper = Paper.query.get(paper_id)
    if not paper:
        return Response.not_found('paper not exist')

    if not paper.attachment_path:
        return Response.not_found('attachment not exist')

    return send_file(
        paper.attachment_path,
        as_attachment=True,
        download_name=paper.title + Path(paper.attachment_path).suffix
    )