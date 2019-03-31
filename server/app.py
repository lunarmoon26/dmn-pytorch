"""
Reference:
https://www.kdnuggets.com/2019/01/build-api-machine-learning-model-using-flask.html
"""

from flask import Flask, request, redirect, url_for, flash, jsonify
import numpy as np
import pickle as p
import json

app = Flask(__name__)


@app.route('/api/talk', methods=['POST'])
def makecalc():
    data = request.get_json()
    prediction = np.array2string(model.predict(data))
    return jsonify(prediction)


if __name__ == '__main__':
    model_file = '../model/model.pickle'
    model = p.load(open(model_file, 'rb'))
    app.run(debug=True, host='0.0.0.0')
