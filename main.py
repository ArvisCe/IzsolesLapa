from flask import Flask, render_template
from routes.blueprintExample import blueprintExample
from routes.authentication import auth
from routes.home import home

app = Flask(__name__)


# example blueprint
app.register_blueprint(blueprintExample, url_prefix="/bp")

# authentication routes >> 
app.register_blueprint(auth, url_prefix="")

# item view and main routes >> 
app.register_blueprint(home, url_prefix="")


if __name__ == "__main__":
    app.run(debug=True)