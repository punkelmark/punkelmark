from flask import Blueprint

views = Blueprint('views', __name__)

@views.route('/') # define decorator for route, default route
def home():
    return "<h1>Test</h1>"