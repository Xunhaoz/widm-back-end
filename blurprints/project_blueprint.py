import os
from uuid import uuid4
import json

from models.project_model import Project, ProjectIcon, db, ProjectTaskImage, ProjectTask
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

        project_payload['project_icon'] = project.project_icon.icon_uuid \
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


@project_blueprint.route('/task/image', methods=['GET'])
def get_project_task_images():
    """
    get project task images
    ---
    tags:
      - project_task_image
    responses:
      200:
        description: get project task images successfully
        schema:
          id: project_task_images
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
        description: project task images not found
    """
    project_task_images = ProjectTaskImage.query.all()
    return Response.response(
        'get project task images successfully',
        [project_task_image.to_dict() for project_task_image in project_task_images]
    )


@project_blueprint.route('/task/image/<project_task_image_uuid>', methods=['GET'])
def get_project_task_image(project_task_image_uuid):
    """
    get project task image
    ---
    tags:
      - project_task_image
    parameters:
      - in: path
        name: project_task_image_uuid
        type: string
        required: true
    responses:
      200:
        description: get project task image successfully
      404:
        description: project task image not found
    """
    project_task_image = ProjectTaskImage.query.filter_by(image_uuid=project_task_image_uuid).first()
    if not project_task_image:
        return Response.not_found("project task image not found")

    return send_file(project_task_image.image_path)


@project_blueprint.route('/task/image', methods=['POST'])
def post_project_task_image():
    """
    post project task image
    ---
    tags:
      - project_task_image
    parameters:
      - in: formData
        name: image
        type: file
        required: true
    responses:
      200:
        description: post project task image successfully
        schema:
          id: project_task_image
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
        description: no ['image'] in files
    """
    image = request.files['image']
    image_uuid = uuid4().hex
    image_name = image.filename
    image_path = f'./statics/images/{image_uuid}.{image_name.split(".")[-1]}'
    image.save(image_path)

    project_task_image = ProjectTaskImage(
        image_uuid=image_uuid,
        image_name=image_name,
        image_path=image_path
    )

    db.session.add(project_task_image)
    db.session.commit()
    return Response.response('post project task image successfully', project_task_image.to_dict())


@project_blueprint.route('/task/image/<project_task_image_uuid>', methods=['DELETE'])
def delete_project_task_image(project_task_image_uuid):
    """
    delete project task image
    ---
    tags:
      - project_task_image
    parameters:
      - in: path
        name: project_task_image_uuid
        type: string
        required: true
    responses:
      200:
        description: delete project task image successfully
        schema:
          id: project_task_image
      404:
        description: project task image not found
    """
    project_task_image = ProjectTaskImage.query.filter_by(image_uuid=project_task_image_uuid).first()
    if not project_task_image:
        return Response.not_found("project task image not found")

    os.remove(project_task_image.image_path)
    db.session.delete(project_task_image)
    db.session.commit()

    return Response.response('delete project task image successfully', project_task_image.to_dict())


class ProjectTaskTreeBuilder:
    def __init__(self, project_tasks):
        self.project_tasks = project_tasks
        self.project_task_pool = {project_task.id: project_task.to_dict() for project_task in project_tasks}
        self.parent_child_map = {}

        self.__build_parent_child_map()
        self.__build_project_task_tree()

    def __build_parent_child_map(self):
        for project_task in self.project_tasks:
            if project_task.id not in self.parent_child_map:
                self.parent_child_map[project_task.id] = []
            if project_task.parent_id not in self.parent_child_map:
                self.parent_child_map[project_task.parent_id] = []
            self.parent_child_map[project_task.parent_id].append(project_task.id)

    def __build_project_task_tree(self):
        building_queue = [0]
        while building_queue:
            next_building_queue = []
            for parent_id in building_queue:
                if parent_id == 0:
                    self.project_task_pool[0] = []
                    for child_id in self.parent_child_map[parent_id]:
                        self.project_task_pool[0].append(self.project_task_pool[child_id])
                        next_building_queue.append(child_id)
                    continue

                self.project_task_pool[parent_id]['children'] = []
                for child_id in self.parent_child_map[parent_id]:
                    self.project_task_pool[parent_id]['children'].append(self.project_task_pool[child_id])
                    next_building_queue.append(child_id)
            building_queue = next_building_queue

@project_blueprint.route('<project_id>/task', methods=['GET'])
def get_project_tasks(project_id):
    """
    get project tasks
    ---
    tags:
      - project_task
    parameters:
      - in: path
        name: project_id
        type: integer
        required: true
    responses:
      200:
        description: get project tasks successfully
        schema:
          id: project_tasks
          properties:
            description:
              type: string
            response:
              type: array
              items:
                properties:
                  id:
                    type: integer
                  project_id:
                    type: integer
                  project_task_title:
                    type: string
                  project_task_sub_title:
                    type: string
                  project_task_content:
                    type: string
                  parent_id:
                    type: integer
                  children:
                    type: array
                    items:
                      properties:
                        id:
                          type: integer
                        project_id:
                          type: integer
                        project_task_title:
                          type: string
                        project_task_sub_title:
                          type: string
                        project_task_content:
                          type: string
                  created_time:
                    type: string
                  updated_time:
                    type: string
      404:
        description: project not found
    """
    if not Project.query.get(project_id):
        return Response.not_found("project not found")

    project_tasks = ProjectTask.query.filter_by(project_id=project_id).all()

    if not project_tasks:
        return Response.response(
        'get project tasks successfully', []
    )

    project_task_tree_builder = ProjectTaskTreeBuilder(project_tasks)
    return Response.response(
        'get project tasks successfully', project_task_tree_builder.project_task_pool[0]
    )


@project_blueprint.route('<project_id>/task/<project_task_id>', methods=['GET'])
def get_project_task(project_id, project_task_id):
    """
    get project task
    ---
    tags:
      - project_task
    parameters:
      - in: path
        name: project_id
        type: integer
        required: true
      - in: path
        name: project_task_id
        type: integer
        required: true
    responses:
      200:
        description: get project task successfully
        schema:
          id: project_task
          properties:
            description:
              type: string
            response:
              properties:
                id:
                  type: integer
                project_id:
                  type: integer
                project_task_title:
                  type: string
                project_task_sub_title:
                  type: string
                project_task_content:
                  type: string
                parent_id:
                  type: integer
                created_time:
                  type: string
                updated_time:
                  type: string
      404:
        description: project not found
    """
    if not Project.query.get(project_id):
        return Response.not_found("project not found")

    project_task = ProjectTask.query.get(project_task_id)
    if not project_task:
        return Response.not_found("project task not found")

    return Response.response('get project task successfully', project_task.to_dict())


@project_blueprint.route('<project_id>/task', methods=['POST'])
def post_project_task(project_id):
    """
    post project task
    ---
    tags:
      - project_task
    parameters:
      - in: path
        name: project_id
        type: integer
        required: true
      - in: body
        name: project_task
        description: project task information
        schema:
          id: project_task_input
          properties:
            project_task_title:
              type: string
            project_task_sub_title:
              type: string
            project_task_content:
              type: string
            parent_id:
              type: integer
    responses:
      200:
        description: post project task successfully
        schema:
          id: project_task
      400:
        description: no ['project_task_title', 'project_task_sub_title', 'project_task_content', 'parent_id'] in json
    """
    if not Project.query.get(project_id):
        return Response.not_found("project not found")

    if not api_input_check(['project_task_title', 'project_task_sub_title', 'project_task_content', 'parent_id'],
                           request.json):
        return Response.client_error(
            "no ['project_task_title', 'project_task_sub_title', 'project_task_content', 'parent_id'] in json")

    project_task_title, project_task_sub_title, project_task_content, parent_id = api_input_get(
        ['project_task_title', 'project_task_sub_title', 'project_task_content', 'parent_id'], request.json
    )

    project_task = ProjectTask(
        project_id=project_id,
        project_task_title=project_task_title,
        project_task_sub_title=project_task_sub_title,
        project_task_content=project_task_content,
        parent_id=parent_id
    )

    db.session.add(project_task)
    db.session.commit()
    return Response.response('post project task successfully', project_task.to_dict())


@project_blueprint.route('<project_id>/task/<project_task_id>', methods=['PATCH'])
def patch_project_task(project_id, project_task_id):
    """
    patch project task
    ---
    tags:
      - project_task
    parameters:
      - in: path
        name: project_id
        type: integer
        required: true
      - in: path
        name: project_task_id
        type: integer
        required: true
      - in: body
        name: project_task
        description: project task information
        schema:
          id: project_task_input
    responses:
      200:
        description: patch project task successfully
        schema:
          id: project_task
      404:
        description: project not found
    """
    if not Project.query.get(project_id):
        return Response.not_found("project not found")

    project_task = ProjectTask.query.get(project_task_id)
    if not project_task:
        return Response.not_found("project task not found")

    if 'project_task_title' in request.json:
        project_task.project_task_title = request.json['project_task_title']
    if 'project_task_sub_title' in request.json:
        project_task.project_task_sub_title = request.json['project_task_sub_title']
    if 'project_task_content' in request.json:
        project_task.project_task_content = request.json['project_task_content']
    if 'parent_id' in request.json:
        project_task.parent_id = request.json['parent_id']

    db.session.commit()
    return Response.response('patch project task successfully', project_task.to_dict())


@project_blueprint.route('<project_id>/task/<project_task_id>', methods=['DELETE'])
def delete_project_task(project_id, project_task_id):
    """
    delete project task
    ---
    tags:
      - project_task
    parameters:
      - in: path
        name: project_id
        type: integer
        required: true
      - in: path
        name: project_task_id
        type: integer
        required: true
    responses:
      200:
        description: delete project task successfully
        schema:
          id: project_task
      404:
        description: project not found
    """
    if not Project.query.get(project_id):
        return Response.not_found("project not found")

    project_task = ProjectTask.query.get(project_task_id)
    if not project_task:
        return Response.not_found("project task not found")

    if ProjectTask.query.filter_by(parent_id=project_task_id).first():
        return Response.client_error("project task has children")

    db.session.delete(project_task)
    db.session.commit()
    return Response.response('delete project task successfully', project_task.to_dict())
