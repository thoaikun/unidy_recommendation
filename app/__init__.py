from flask import Flask

app = Flask(__name__)

# app.config.from_object('app.config')

from app.routes import recommend_routes
app.register_blueprint(recommend_routes)

# from app.models import user, post

