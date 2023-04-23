from flask import Blueprint, render_template

blueprintExample = Blueprint("blueprintExample", __name__, static_folder="static", template_folder="templates")

@blueprintExample.route("/home")
def home():
    return "<h1>Blueprint home page!</h1><br><a href='/bp'> click to go back </a>"

@blueprintExample.route("/")
def index():
    return "<h1>This is an example for blueprints in Flask!</h1><a href='home'> click to go to home </a>"