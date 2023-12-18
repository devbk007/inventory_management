from flask import Flask
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///your_database.db'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:postgres@localhost/inventory_management'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# import views
from views import *

# main driver function
if __name__ == '__main__':
  app.run(debug = True)