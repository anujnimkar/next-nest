import os

from flask import Flask

from config import Config


def create_app(config_class=Config):
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    app = Flask(
        __name__,
        template_folder=os.path.join(root, "templates"),
        static_folder=os.path.join(root, "static"),
    )
    app.config.from_object(config_class)

    from app.routes import bp

    app.register_blueprint(bp)
    return app
