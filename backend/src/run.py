import os
from flask_migrate import Migrate
from . import create_app, db
from .entities.user import User
from .entities.role import Role

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
migrate = Migrate(app, db)


@app.shell_context_processor
def make_shell_context():
    return dict(db=db, User=User, Role=Role)