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


class ProjectIcon(db.Model, SchemaMixin):
    __tablename__ = 'project_icon'
    project_id = db.Column(db.Integer, db.ForeignKey('project.id', ondelete="CASCADE"), unique=True)
    icon_uuid = db.Column(db.String(255))
    icon_name = db.Column(db.String(255))
    icon_path = db.Column(db.String(255))
