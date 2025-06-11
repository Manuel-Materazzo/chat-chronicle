from flask import Flask
from flask_smorest import Api
from src.controller.summary_controller import blp as summary_blp, set_config

app = Flask(__name__)
app.config["API_TITLE"] = "Chat Chronicle"
app.config["API_VERSION"] = "v1"
app.config["OPENAPI_VERSION"] = "3.0.3"
app.config["OPENAPI_URL_PREFIX"] = "/"
app.config["OPENAPI_SWAGGER_UI_PATH"] = "/swagger-ui"
app.config["OPENAPI_SWAGGER_UI_URL"] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"

api = Api(app)
api.register_blueprint(summary_blp)


def start_server(config: dict):
    from waitress import serve
    set_config(config)
    serve(app, host="0.0.0.0", port=8000)
