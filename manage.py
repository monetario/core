#!/usr/bin/env python

from flask import Flask
from flask.ext.script import Manager, prompt, prompt_pass, Shell

app = Flask(__name__)
manager = Manager(app)

@app.route("/")
def hello():
    return "Hello World!"

if __name__ == '__main__':
    manager.run()
