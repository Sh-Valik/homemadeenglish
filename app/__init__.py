import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()
migrate = Migrate()


def create_app():
    app = Flask(
        __name__,
        template_folder=os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates"),
        static_folder=os.path.join(os.path.dirname(os.path.dirname(__file__)), "static"),
    )
    app.config.from_object("config.Config")

    # Ensure instance directory exists
    instance_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "instance")
    os.makedirs(instance_dir, exist_ok=True)

    db.init_app(app)
    migrate.init_app(app, db)

    # Register blueprints
    from app.routes.main import main_bp
    from app.routes.topics import topics_bp
    from app.routes.practice import practice_bp
    from app.routes.auth import auth_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(topics_bp, url_prefix="/api")
    app.register_blueprint(practice_bp, url_prefix="/api")
    app.register_blueprint(auth_bp, url_prefix="/api")

    # Create tables
    with app.app_context():
        from app import models  # noqa: F401
        # db.create_all() removed for flask-migrate

    return app
