from flask import Flask
from flask_cors import CORS
from config import configure_app, db
from auth.auth_bp import auth_bp
from user.user_bp import user_bp

app = Flask(__name__)
configure_app(app)
CORS(app)

app.register_blueprint(auth_bp, url_prefix="/auth")
app.register_blueprint(user_bp, url_prefix="/user")

#Default Route
@app.route('/')
def hello():
    return "Hello World! Let's Get Started With This Then, Shall We?"

if __name__ == "__main__":
    app.run(debug=True)
