from flask import Flask
from flask import render_template

app = Flask(__name__)

@app.route('/')
def Index():
    return render_template('../frontend/index.html')