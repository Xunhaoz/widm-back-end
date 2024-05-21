from models.database import *


class Member(db.Model, SchemaMixin):
    __tablename__ = 'member'
    member_name = db.Column(db.String(255))
    member_intro = db.Column(db.String(255))
    member_character = db.Column(db.String(255))

    member_image = db.relationship(
        'MemberImage', backref='member', lazy='select', uselist=False, cascade="all, delete-orphan"
    )


class MemberImage(db.Model, SchemaMixin):
    __tablename__ = 'member_image'
    member_id = db.Column(db.Integer, db.ForeignKey('member.id', ondelete="CASCADE"), unique=True)
    image_uuid = db.Column(db.String(255))
    image_name = db.Column(db.String(255))
    image_path = db.Column(db.String(255))
