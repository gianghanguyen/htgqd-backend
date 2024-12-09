from sanic import Blueprint

from app.apis.calculate_blueprint import calculate_bp
from app.apis.info_blueprint import info_bp

api = Blueprint.group(
    calculate_bp, info_bp
)
