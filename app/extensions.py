from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_bootstrap import Bootstrap

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
bootstrap = Bootstrap()

# Initialize extensions
# db = SQLAlchemy()
# migrate = Migrate()
# bootstrap = Bootstrap()
# login_manager = LoginManager()