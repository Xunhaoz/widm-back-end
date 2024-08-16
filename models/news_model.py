from models.database import *


class News(db.Model, SchemaMixin):
    __tablename__ = 'news'
    title = db.Column(db.String(255))
    sub_title = db.Column(db.String(255))
    content = db.Column(db.Text)


