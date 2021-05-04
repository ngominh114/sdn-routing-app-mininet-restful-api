from flask import Flask
app = Flask(__name__)

@app.route('/devices')
def get_devices():
    return 