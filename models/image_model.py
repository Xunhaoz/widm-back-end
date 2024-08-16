import os
from models.database import *


class Image(db.Model, SchemaMixin):
    __tablename__ = 'image'
    image_name = db.Column(db.String(100))
    image_path = db.Column(db.String(255))

    def to_dict(self):
        return {
            "file": str(self.id),
            "name": self.image_name,
            "type": "image",
            "thumb": str(self.id),
            "changed": self.create_time.strftime('%Y-%m-%d %I:%M:%S %p'),
            "size": os.path.getsize(self.image_path),
            "isImage": True
        }
