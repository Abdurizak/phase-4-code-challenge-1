from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, create_access_token,create_refresh_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, Item,TokenBlocklist
from flask_migrate import Migrate
from datetime import timedelta
from Views import *

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['JWT_SECRET_KEY'] = 'your_jwt_secret_key'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)
jwt = JWTManager(app)


# Initialize extensions
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///items.db'
db.init_app(app)
migrate = Migrate(app, db)

app.register_blueprint(User_bp)
app.register_blueprint(Item_bp)

@jwt.token_in_blocklist_loader
def check_if_token_revoked(jwt_header, jwt_payload: dict) -> bool:
    jti = jwt_payload["jti"]
    token = db.session.query(TokenBlocklist.id).filter_by(jti=jti).scalar()

    return token is not None
 
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)