import os
import json
from uuid import uuid4
from pathlib import Path
from json import dumps

from models.project_model import Project, db, ProjectTask
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
            name:
              example: name
              type: string
            description:
              example: description
              type: string
            tags:
              example: ['tag1', 'tag2']
              type: array
            link:
              example: 'http://www.example.com'
              type: string
            github:
              example: 'http://www.example.com'
              type: string
            members:
              example: ['member1', 'member2']
              type: array
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
                name:
                  example: name
                  type: string
                description:
                  example: description
                  type: string
                tags:
                  example: ['tag1', 'tag2']
                  type: array
                link:
                  example: 'http://www.example.com'
                  type: string
                github:
                  example: 'http://www.example.com'
                  type: string
                members:
                  example: ['member1', 'member2']
                  type: array
                created_time:
                  example: 'Tue, 06 Aug 2024 10:39:27 GMT'
                  type: string
                updated_time:
                  example: 'Tue, 06 Aug 2024 10:39:27 GMT'
                  type: string
      400:
        description: no ['project_name'] in json
    """
    if not api_input_check(['name', 'description', 'tags', 'link', 'github', 'members'], request.json):
        return Response.client_error("no ['name', 'description', 'tags', 'link', 'github', 'members'] in json")

    name, description, tags, link, github, members = api_input_get(
        ['name', 'description', 'tags', 'link', 'github', 'members'], request.json)

    tags = dumps(tags)
    members = dumps(members)

    project = Project(
        name=name,
        description=description,
        tags=tags,
        link=link,
        github=github,
        members=members,
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
                  name:
                    example: name
                    type: string
                  description:
                    example: description
                    type: string
                  tags:
                    example: ['tag1', 'tag2']
                    type: array
                  link:
                    example: 'http://www.example.com'
                    type: string
                  github:
                    example: 'http://www.example.com'
                    type: string
                  members:
                    example: ['member1', 'member2']
                    type: array
                  created_time:
                    example: 'Tue, 06 Aug 2024 10:39:27 GMT'
                    type: string
                  updated_time:
                    example: 'Tue, 06 Aug 2024 10:39:27 GMT'
                    type: string
    """
    projects = Project.query.all()
    return Response.response('get projects successfully', [project.to_dict() for project in projects])


@project_blueprint.route('<project_id>', methods=['GET'])
def get_project(project_id):
    """
    get project
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
        description: get project successfully
        schema:
          id: project
      404:
        description: project not found
    """
    project = Project.query.get(project_id)
    if not project:
        return Response.not_found("project not found")

    return Response.response('get project successfully', project.to_dict())


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

    if project.icon_path:
        os.remove(project.icon_path)

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

    if 'name' in request.json:
        project.name = request.json['name']
    if 'description' in request.json:
        project.description = request.json['description']
    if 'tags' in request.json:
        project.tags = dumps(request.json['tags'])
    if 'link' in request.json:
        project.link = request.json['link']
    if 'github' in request.json:
        project.github = request.json['github']
    if 'members' in request.json:
        project.members = json.dumps(request.json['members'])

    db.session.commit()
    return Response.response('patch project successfully', project.to_dict())


@project_blueprint.route('<project_id>/project-icon', methods=['POST'])
def post_project_icon(project_id):
    """
    post project icon
    ---
    tags:
      - project
    parameters:
      - in: path
        name: project_id
        type: integer
        required: true
      - in: formData
        name: image
        type: file
        required: true
    responses:
      200:
        description: post project icon successfully
        schema:
          id: project
      400:
        description: no ['image'] in files
      404:
        description: project not found
    """

    if not api_input_check(['image'], request.files):
        return Response.client_error("no ['image'] in files")

    project = Project.query.get(project_id)
    if not project:
        Response.not_found("project not found")

    if project.icon_path:
        os.remove(project.icon_path)

    image = request.files['image']
    icon_uuid = uuid4().hex
    icon_name = image.filename
    icon_path = f'./statics/images/{icon_uuid}.{icon_name.split(".")[-1]}'
    image.save(icon_path)
    project.icon_path = str(icon_path)

    db.session.commit()
    return Response.response('post project icon successfully', project.to_dict())


@project_blueprint.route('<project_id>/project-icon', methods=['GET'])
def get_project_icon(project_id):
    """
    get project icon
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
        description: get project icon successfully
      404:
        description: project not found
    """
    project = Project.query.get(project_id)
    if not project:
        return Response.not_found("project not found")

    if not project.icon_path:
        return Response.not_found("project icon not found")

    return send_file(project.icon_path)


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
                  example: 1
                  type: integer
                title:
                  example: title
                  type: string
                sub_title:
                  example: sub_title
                  type: string
                members:
                  example: ['member1', 'member2']
                  type: array
                content:
                  example: content
                  type: string
                papers:
                  example: ['paper1', 'paper2']
                  type: array
                project_id:
                  example: 1
                  type: integer
                parent_id:
                  example: 1
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
    if this task is a child task, parent_id should be set to the parent task id
    if not parent_id should be set to 0
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
            title:
              example: title
              type: string
            sub_title:
              example: sub_title
              type: string
            members:
              example: ['member1', 'member2']
              type: array
            content:
              example: content
              type: string
            papers:
              example: ['paper1', 'paper2']
              type: array
            parent_id:
              example: 0
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

    if not api_input_check([
        'title', 'sub_title', 'members', 'content', 'papers', 'parent_id'
    ], request.json):
        return Response.client_error(
            "no ['title', 'sub_title', 'members', 'content', 'papers', 'parent_id'] in json")

    title, sub_title, members, content, papers, parent_id = api_input_get(
        ['title', 'sub_title', 'members', 'content', 'papers', 'parent_id'], request.json
    )
    members = dumps(members)
    papers = dumps(papers)

    project_task = ProjectTask(
        title=title,
        sub_title=sub_title,
        members=members,
        content=content,
        papers=papers,
        project_id=project_id,
        parent_id=parent_id,
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

    if 'title' in request.json:
        project_task.title = request.json['title']
    if 'sub_title' in request.json:
        project_task.sub_title = request.json['sub_title']
    if 'members' in request.json:
        project_task.members = dumps(request.json['members'])
    if 'content' in request.json:
        project_task.content = request.json['content']
    if 'papers' in request.json:
        project_task.papers = dumps(request.json['papers'])
    if 'project_id' in request.json:
        project_task.project_id = request.json['project_id']
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
