from models.database import *


class News(db.Model, SchemaMixin):
    __tablename__ = 'news'
    news_title = db.Column(db.String(255))
    news_sub_title = db.Column(db.String(255))
    news_content = db.Column(db.Text)


class NewsImage(db.Model, SchemaMixin):
    __tablename__ = 'news_image'
    image_uuid = db.Column(db.String(255))
    image_name = db.Column(db.String(255))
    image_path = db.Column(db.String(255))
