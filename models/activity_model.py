from models.database import *


class Activity(db.Model, SchemaMixin):
    __tablename__ = 'activity'
    title = db.Column(db.String(50))
    sub_title = db.Column(db.Text)
    date = db.Column(db.DateTime)

    activity_image = db.relationship('ActivityImage', backref='activity')

    def to_dict(self):
        self.date = datetime.strftime(self.date, '%Y-%m-%d') if self.date else None
        result = {
            "id": self.id,
            "title": self.title,
            "sub_title": self.sub_title,
            "date": self.date,
            "images": [image.id for image in self.activity_image],
            "create_time": self.create_time,
            "update_time": self.update_time
        }
        return result


class ActivityImage(db.Model, SchemaMixin):
    __tablename__ = 'activity_image'
    activity_id = db.Column(db.Integer, db.ForeignKey('activity.id'))
    image_path = db.Column(db.String(255))
