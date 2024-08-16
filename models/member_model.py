from models.database import *
from datetime import datetime


class Member(db.Model, SchemaMixin):
    __tablename__ = 'member'
    name = db.Column(db.String(50), nullable=False)
    name_en = db.Column(db.String(50), nullable=False)
    position = db.Column(db.String(50), nullable=False)
    intro = db.Column(db.Text, nullable=False)
    image_path = db.Column(db.String(255), nullable=True)
    graduate_year = db.Column(db.DateTime, nullable=True)

    def to_dict(self):
        self.graduate_year = datetime.strftime(self.graduate_year, '%Y-%m') if self.graduate_year else None
        image_existed = True if self.image_path else False
        return {
            'id': self.id,
            'name': self.name,
            'name_en': self.name_en,
            'position': self.position,
            'intro': self.intro,
            'graduate_year': self.graduate_year,
            'image_existed': image_existed,
            'create_time': self.create_time,
            'update_time': self.update_time
        }
