import os

from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy

from pending_afip import agrupar_prefacturas

DB_USER = os.environ.get('DB_USER')
DB_PASSWORD = os.environ.get('DB_PASSWORD')
DB_NAME = os.environ.get('DB_NAME')
DB_HOST = os.environ.get('DB_HOST')
DB_PORT = os.environ.get('DB_PORT')

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Cliente(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f'<Cliente {self.nombre}>'

with app.app_context():
    db.create_all()

@app.route('/clientes')
def index():
    clientes = Cliente.query.all()
    return '<br>'.join([c.nombre for c in clientes])


@app.route('/')
def hello():
    return jsonify(agrupar_prefacturas())

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8888)
