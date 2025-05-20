from flask import Flask, jsonify

from pending_afip import agrupar_prefacturas


app = Flask(__name__)


@app.route('/')
def hello():
    return jsonify(agrupar_prefacturas())

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
