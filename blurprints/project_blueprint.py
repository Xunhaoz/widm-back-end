import os
from uuid import uuid4
import json

from models.project_model import Project, ProjectIcon, db
from models.responses import Response
from utiles.api_helper import *

from flask import Blueprint, request, send_file
from sqlalchemy.orm import joinedload

project_blueprint = Blueprint('project', __name__)


@project_blueprint.route('', methods=['POST'])
def post_project():
    """
    post project
    ---
    tags:
      - project
    parameters:
      - in: body
        name: project
        description: project information
        schema:
          id: project_input
          properties:
            project_name:
              type: string
            project_description:
              type: string
            project_link:
              type: string
            project_github:
              type: string
            project_tags:
              type: array
              items:
                type: string
    responses:
      200:
        description: post project successfully
        schema:
          id: project
          properties:
            description:
              type: string
            response:
              properties:
                id:
                  type: integer
                project_name:
                  type: string
                project_description:
                  type: string
                project_link:
                  type: string
                project_github:
                  type: string
                project_tags:
                  type: array
                  items:
                    type: string
                created_time:
                  type: string
                updated_time:
                  type: string
      400:
        description: no ['project_name'] in json
    """
    if not api_input_check(['project_name'], request.json):
        return Response.client_error("no ['project_name'] in json")

    project = Project(
        project_name=request.json['project_name'],
        project_description=request.json.get('project_description', None),
        project_link=request.json.get('project_link', None),
        project_github=request.json.get('project_github', None),
        project_tags=json.dumps(request.json['project_tags']) if 'project_tags' in request.json else None,
    )
    db.session.add(project)
    db.session.commit()
    return Response.response('post project successfully', project.to_dict())


@project_blueprint.route('', methods=['GET'])
def get_projects():
    """
    get projects
    ---
    tags:
      - project
    responses:
      200:
        description: get projects successfully
        schema:
          id: projects
          properties:
            description:
              type: string
            response:
              type: array
              items:
                properties:
                  id:
                    type: integer
                  project_name:
                    type: string
                  project_description:
                    type: string
                  project_link:
                    type: string
                  project_github:
                    type: string
                  project_tags:
                    type: array
                    items:
                      type: string
                  created_time:
                    type: string
                  updated_time:
                    type: string
                  member_image:
                    type: string
    """
    projects = (
        Project.query
        .options(joinedload(Project.project_icon))
    ).all()

    projects_payload = []
    for project in projects:
        project_payload = project.to_dict()

        if project_payload['project_tags']:
            project_payload['project_tags'] = json.loads(project_payload['project_tags'])

        project_payload['member_image'] = project.project_icon.icon_uuid \
            if project.project_icon else None

        projects_payload.append(project_payload)

    return Response.response('get projects successfully', projects_payload)


@project_blueprint.route('<project_id>', methods=['DELETE'])
def delete_projects(project_id):
    """
    delete project
    ---
    tags:
      - project
    parameters:
      - in: path
        name: project_id
        type: integer
        required: true
    responses:
      200:
        description: delete project successfully
        schema:
          id: project
      404:
        description: project not found
    """
    project = Project.query.get(project_id)
    if not project:
        return Response.not_found("project not found")

    project_icon = ProjectIcon.query.filter_by(project_id=project_id).first()
    if project_icon:
        os.remove(project_icon.icon_path)

    db.session.delete(project)
    db.session.commit()
    return Response.response('delete project successfully', project.to_dict())


@project_blueprint.route('<project_id>', methods=['PATCH'])
def patch_project(project_id):
    """
    patch project
    ---
    tags:
      - project
    parameters:
      - in: path
        name: project_id
        type: integer
        required: true
      - in: body
        name: project
        description: project information
        schema:
          id: project_input
    responses:
      200:
        description: patch project successfully
        schema:
          id: project
      404:
        description: project not found
    """
    project = Project.query.get(project_id)
    if not project:
        return Response.not_found("project not found")

    if 'project_name' in request.json:
        project.project_name = request.json['project_name']
    if 'project_description' in request.json:
        project.project_description = request.json['project_description']
    if 'project_link' in request.json:
        project.project_link = request.json['project_link']
    if 'project_github' in request.json:
        project.project_github = request.json['project_github']
    if 'project_tags' in request.json:
        project.project_tags = json.dumps(request.json['project_tags'])

    db.session.commit()
    return Response.response('patch project successfully', project.to_dict())


@project_blueprint.route('<project_id>/project-icon', methods=['POST'])
def post_project_icon(project_id):
    """
    post project icon
    ---
    tags:
      - project_icon
    parameters:
      - in: path
        name: project_id
        type: integer
        required: true
      - in: formData
        name: project_icon
        type: file
        required: true
    responses:
      200:
        description: post project icon successfully
        schema:
          id: project_icon
          properties:
            description:
              type: string
            response:
              properties:
                id:
                  type: integer
                project_id:
                  type: integer
                icon_uuid:
                  type: string
                icon_name:
                  type: string
                icon_path:
                  type: string
                created_time:
                  type: string
                updated_time:
                  type: string
      400:
        description: no ['project_icon'] in files
      404:
        description: project not found
    """
    if not api_input_check(['project_icon'], request.files):
        return Response.client_error("no ['project_icon'] in files")

    if not Project.query.get(project_id):
        Response.not_found("project not found")

    if ProjectIcon.query.filter_by(project_id=project_id).first():
        return Response.client_error("only one image is allowed")

    image = request.files['project_icon']
    icon_uuid = uuid4().hex
    icon_name = image.filename
    icon_path = f'./statics/images/{icon_uuid}.{icon_name.split(".")[-1]}'
    image.save(icon_path)

    project_icon = ProjectIcon(
        project_id=project_id,
        icon_uuid=icon_uuid,
        icon_name=icon_name,
        icon_path=icon_path
    )

    db.session.add(project_icon)
    db.session.commit()
    return Response.response('post project icon successfully', project_icon.to_dict())


@project_blueprint.route('<project_id>/project-icon/<project_icon_uuid>', methods=['DELETE'])
def delete_project_icon(project_id, project_icon_uuid):
    """
    delete project icon
    ---
    tags:
      - project_icon
    parameters:
      - in: path
        name: project_id
        type: integer
        required: true
      - in: path
        name: project_icon_uuid
        type: string
        required: true
    responses:
      200:
        description: delete project icon successfully
        schema:
          id: project_icon
      404:
        description: project not found
    """
    if not Project.query.get(project_id):
        return Response.not_found("project not found")

    project_icon = ProjectIcon.query.filter_by(icon_uuid=project_icon_uuid).first()
    if not project_icon:
        return Response.not_found("project icon not found")

    os.remove(project_icon.icon_path)
    db.session.delete(project_icon)
    db.session.commit()

    return Response.response('delete project icon successfully', project_icon.to_dict())


@project_blueprint.route('<project_id>/project-icon/<project_icon_uuid>', methods=['GET'])
def get_project_icon(project_id, project_icon_uuid):
    """
    get project icon
    ---
    tags:
      - project_icon
    parameters:
      - in: path
        name: project_id
        type: integer
        required: true
      - in: path
        name: project_icon_uuid
        type: string
        required: true
    responses:
      200:
        description: get project icon successfully
      404:
        description: project not found
    """
    if not Project.query.get(project_id):
        return Response.not_found("project not found")

    project_icon = ProjectIcon.query.filter_by(icon_uuid=project_icon_uuid).first()
    if not project_icon:
        return Response.not_found("project icon not found")

    return send_file(project_icon.icon_path)
