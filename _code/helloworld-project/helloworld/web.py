from flask import Flask, render_template
from helloworld.core import get_message


app = Flask(__name__)


@app.route("/")
def hello():
    return render_template('index.html',
        message=get_message())


def run_server():
    app.run()
