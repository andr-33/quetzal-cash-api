import os
from flask import Flask, request, jsonify
from dotenv import load_dotenv

load_dotenv()
PORT = os.getenv('PORT')
DEBUG = os.getenv('FLASK_DEBUG')

app = Flask(__name__)

if __name__ == '__main__':
    app.run(debug=DEBUG, port=PORT)