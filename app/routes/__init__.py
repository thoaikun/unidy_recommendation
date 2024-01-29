from flask import Flask

app = Flask(__name__)

from app.routes.recommend_routes import recommend_routes

app.register_blueprint(recommend_routes)
