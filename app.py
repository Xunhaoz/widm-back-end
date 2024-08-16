from pathlib import Path
import uuid
import pymysql

from blurprints.member_blueprint import member_blueprint
from blurprints.image_blueprint import image_blueprint
from blurprints.activity_blueprint import activity_blueprint
from blurprints.paper_blueprint import paper_blueprint
from blurprints.project_blueprint import project_blueprint
from blurprints.retrieval_blueprint import retrieval_blueprint
from blurprints.news_blueprint import news_blueprint
from blurprints.auth_blueprint import auth_blueprint

from config import Config
from models.database import db

from flask import Flask, session, render_template
from flasgger import Swagger
from flask_cors import CORS


def create_app(status='development'):
    app = Flask(__name__)
    app.secret_key = uuid.uuid4().hex
    app.config.from_object(Config)
    db.init_app(app)

    app.register_blueprint(member_blueprint, url_prefix='/member')
    app.register_blueprint(image_blueprint, url_prefix='/image')
    app.register_blueprint(activity_blueprint, url_prefix='/activity')
    app.register_blueprint(paper_blueprint, url_prefix='/paper')
    app.register_blueprint(project_blueprint, url_prefix='/project')
    app.register_blueprint(retrieval_blueprint, url_prefix='/retrieval')
    app.register_blueprint(news_blueprint, url_prefix='/news')
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    Swagger(app)
    CORS(
        app,
        resources={
            r"/*": {
                "origins": "*", "allow_headers": "*", "expose_headers": "*"
            }
        },
    )

    return app


app = create_app()

if __name__ == '__main__':
    Path('statics/images').mkdir(parents=True, exist_ok=True)
    Path('statics/attachments').mkdir(parents=True, exist_ok=True)
    app.run(host=app.config['HOST'], port=app.config['PORT'])
