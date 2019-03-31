"""
Reference:
https://www.kdnuggets.com/2019/01/build-api-machine-learning-model-using-flask.html
"""

from flask import Flask, request, jsonify
import numpy as np
import pickle as p
import json

app = Flask(__name__)


@app.route("/api/ask", methods=["POST"])
def answer():
    data = request.get_json()
    if model:
        ans = model.predict(data)
        prediction = np.array2string(ans)
    else:
        prediction = {"error": "no module is available"}
    resp = jsonify(prediction)
    return resp


@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def default_answer(path):
    return "this address {} is not available".format(path)


def load_model():
    try:
        model_file = "../model/model.pickle"
        model = p.load(open(model_file, "rb"))
        return model
    except:
        return None


if __name__ == "__main__":
    model = load_model()
    app.run(debug=True, host="0.0.0.0")
