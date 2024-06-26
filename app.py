import uuid
import logging

from blurprints.paper_blueprint import paper_blueprint
from blurprints.member_blueprint import member_blueprint
from blurprints.activity_blueprint import activity_blueprint
from blurprints.project_blueprint import project_blueprint
from blurprints.news_blueprint import news_blueprint

from config import DevelopmentConfig, ProductionConfig, TestConfig
from models.database import db

from flask import Flask, session, render_template
from flasgger import Swagger
from flask_cors import CORS


def create_app(status='development'):
    app = Flask(__name__)
    app.secret_key = uuid.uuid4().hex

    if status == 'development':
        app.config.from_object(DevelopmentConfig)
    elif status == 'testing':
        app.config.from_object(TestConfig)
    elif status == 'production':
        app.config.from_object(ProductionConfig)

    db.init_app(app)

    if app.config['DEBUG']:
        logging.basicConfig(
            filename=app.config['LOGGING_FILENAME'], level=app.config['LOGGING_LEVEL'],
            format=app.config['LOGGING_FORMAT']
        )

    with app.app_context():
        # db.drop_all()
        db.create_all()
        db.session.commit()

    app.register_blueprint(paper_blueprint, url_prefix='/paper')
    app.register_blueprint(member_blueprint, url_prefix='/member')
    app.register_blueprint(activity_blueprint, url_prefix='/activity')
    app.register_blueprint(project_blueprint, url_prefix='/project')
    app.register_blueprint(news_blueprint, url_prefix='/news')

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
    app.run(host=app.config['HOST'], port=app.config['PORT'])
