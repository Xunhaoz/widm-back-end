from models.database import *


class Activity(db.Model, SchemaMixin):
    __tablename__ = 'activity'
    activity_title = db.Column(db.String(255))
    activity_sub_title = db.Column(db.String(255))

    activity_image = db.relationship(
        'ActivityImage', backref='activity', lazy='select', cascade="all, delete-orphan"
    )


class ActivityImage(db.Model, SchemaMixin):
    __tablename__ = 'activity_image'
    activity_id = db.Column(db.Integer, db.ForeignKey('activity.id', ondelete="CASCADE"))
    image_uuid = db.Column(db.String(255))
    image_name = db.Column(db.String(255))
    image_path = db.Column(db.String(255))
