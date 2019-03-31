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
def ask():
    """
    {
        "question": "string",
        "user_id": "string",
    }
    :return:
    """
    data = request.get_json()

    if data['user_id'] not in input_dict:
        return "this user does not have any action yet"

    input_dict[data['user_id']].append(data['question'])

    if model:
        ans = model.predict(data)
        prediction = np.array2string(ans)
    else:
        prediction = {"error": "no module is available"}
    resp = jsonify(prediction)
    return resp


@app.route("/api/action", methods=["POST"])
def input_action():
    """
    {
        "action": "left|right|up|down",
        "user_id": "string",
    }
    :return:
    """
    # frontend post user actions in this api, actions are the input of input model

    data = request.get_json()

    # save action into dict and later will be sent to model along with question
    if data['user_id'] in input_dict:
        input_dict[data['user_id']].append(data['action'])
    else:
        input_dict[data['user_id']] = [data['action']]

    print(input_dict)

    return "successfully update"


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

    # user_id -> input data list
    input_dict = {
        "dummy_id": ["data", "question"]
    }
    app.run(debug=True, host="0.0.0.0")
