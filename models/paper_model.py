from models.database import *


class Paper(db.Model, SchemaMixin):
    __tablename__ = 'paper'
    paper_publish_year = db.Column(db.Integer, nullable=True)
    paper_title = db.Column(db.String(255))
    paper_origin = db.Column(db.String(255), nullable=True)
    paper_link = db.Column(db.String(255), nullable=True)
    paper_tags = db.Column(db.String(255), nullable=True)
    paper_authors = db.Column(db.String(255), nullable=True)

    paper_attachment = db.relationship(
        'PaperAttachment', backref='paper', lazy='select', cascade="all, delete-orphan", uselist=False
    )


class PaperAttachment(db.Model, SchemaMixin):
    __tablename__ = 'paper_attachment'
    paper_id = db.Column(db.Integer, db.ForeignKey('paper.id', ondelete="CASCADE"), unique=True)
    attachment_uuid = db.Column(db.String(255))
    attachment_name = db.Column(db.String(255))
    attachment_path = db.Column(db.String(255))
