from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from .config import Config 
from .models import db
from .routes import routes_blueprint
from flask_cors import CORS
app = Flask(__name__)
CORS(app)
app.config.from_object(Config)

db.init_app(app)
migrate = Migrate(app, db)

def create_db():
    with app.app_context():
        db.create_all()

create_db()

app.register_blueprint(routes_blueprint)

if __name__ == '__main__':
    app.run(debug=True)

    
