from flask import Flask
from flask_cors import CORS
from config import configure_app, db
from auth.auth_bp import auth_bp
from user.user_bp import user_bp

app = Flask(__name__)
configure_app(app)   #this fucntion is defined in config.py and sets up the flask app,db,swagger and flask migrate
CORS(app) #cross origin resource sharing, enables flask backend to be accessed by the frontend

app.register_blueprint(auth_bp, url_prefix="/auth") #registering auth blueprint
app.register_blueprint(user_bp, url_prefix="/user") #registering user blueprint

#Default Route
@app.route('/')
def hello():
    return "Hello World! Let's Get Started With This Then, Shall We?"

if __name__ == "__main__":
    app.run(debug=True)
