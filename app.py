from flask import Flask
from flask_cors import CORS
from config import configure_app, db
from blueprints.auth.auth_bp import auth_bp
from blueprints.user.user_bp import user_bp
from blueprints.ai.ai_bp import ai_bp
from blueprints.meeting.meeting_bp import meeting_bp

app = Flask(__name__)
configure_app(app)   #this fucntion is defined in config.py and sets up the flask app,db,swagger and flask migrate
CORS(app) #cross origin resource sharing, enables flask backend to be accessed by the frontend

app.register_blueprint(auth_bp, url_prefix="/auth") #registering auth blueprint
app.register_blueprint(user_bp, url_prefix="/user") #registering user blueprint
app.register_blueprint(ai_bp, url_prefix='/ai')
app.register_blueprint(meeting_bp, url_prefix='/meeting')

#Default Route
@app.route('/')
def hello():
    return "Hello World! Let's Get Started With This Then, Shall We?"

with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)
