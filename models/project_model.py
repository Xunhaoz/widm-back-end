from models.database import *


class Project(db.Model, SchemaMixin):
    __tablename__ = 'project'
    project_name = db.Column(db.String(255), nullable=True)
    project_description = db.Column(db.String(255), nullable=True)
    project_link = db.Column(db.String(255), nullable=True)
    project_github = db.Column(db.String(255), nullable=True)
    project_tags = db.Column(db.String(255), nullable=True)

    project_icon = db.relationship(
        'ProjectIcon', backref='member', lazy='select', uselist=False, cascade="all, delete-orphan"
    )
    project_task = db.relationship(
        'ProjectTask', backref='member', lazy='select', cascade="all, delete-orphan"
    )


class ProjectIcon(db.Model, SchemaMixin):
    __tablename__ = 'project_icon'
    project_id = db.Column(db.Integer, db.ForeignKey('project.id', ondelete="CASCADE"), unique=True)
    icon_uuid = db.Column(db.String(255))
    icon_name = db.Column(db.String(255))
    icon_path = db.Column(db.String(255))


class ProjectTask(db.Model, SchemaMixin):
    __tablename__ = 'project_task'
    project_id = db.Column(db.Integer, db.ForeignKey('project.id', ondelete="CASCADE"))
    parent_id = db.Column(db.Integer, nullable=True)
    project_task_title = db.Column(db.String(255))
    project_task_sub_title = db.Column(db.String(255))
    project_task_content = db.Column(db.Text)



class ProjectTaskImage(db.Model, SchemaMixin):
    __tablename__ = 'project_task_image'
    image_uuid = db.Column(db.String(255))
    image_name = db.Column(db.String(255))
    image_path = db.Column(db.String(255))
