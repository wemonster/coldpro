from flask import Blueprint


admin = Blueprint('admin', __name__)
from text.admin import views