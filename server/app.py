"""
Reference:
https://www.kdnuggets.com/2019/01/build-api-machine-learning-model-using-flask.html
"""
import sys
import argparse
import pickle
import pprint

import torch
from torch.autograd import Variable
import numpy as np
import nltk
from flask import Flask, request, jsonify
from flask_cors import CORS

from dataset import Dataset, Config
from model import DMN
from run import run_epoch
from config import get_default_args

args = get_default_args()
args.set_num = 0 # force set_num to be 0

app = Flask(__name__)
CORS(app)
model_proxy = None

@app.route("/api/ask", methods=["POST"])
def ask():
    """
    {
        "question": "string",
        "user_id": "string",
    }
    """
    data = request.form

    if data["user_id"] not in input_dict:
        return "this user does not have any action yet"

    input_dict[data["user_id"]].append(data["question"])

    if model:
        ans = model.predict(data)
        prediction = np.array2string(ans)
    else:
        prediction = "no module is available"

    # clean user actions
    input_dict[data["user_id"]] = []

    resp = jsonify({"answer": prediction})
    return resp


@app.route("/api/action", methods=["POST"])
def input_action():
    """
    {
        "action": "left|right|up|down",
        "user_id": "string",
    }
    """
    # frontend post user actions in this api, actions are the input of input model
    data = request.form

    # save action into dict and later will be sent to model along with question
    if data["user_id"] in input_dict:
        input_dict[data["user_id"]].append(data["action"])
    else:
        input_dict[data["user_id"]] = [data["action"]]

    print(input_dict)

    return "successfully update"


@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def default_answer(path):
    return "this address {} is not available".format(path)
    
class ModelProxy(object):
    def __init__(self, model, dataset):
        self.model = model
        self.dataset = dataset
    def predict(self, lines):
        self.dataset.process_input(lines)
        _, answers = run_epoch(self.model, self.dataset, 0, 'te', 0, False)
        ans = [self.dataset.idx2word[an] for an in answers]
        print(ans)

def init_model():
    global model_proxy
    try:
        dataset = pickle.load(open(args.data_path, 'rb'))

        # Merge and update config pamameters
        dataset.config.__dict__.update(args.__dict__)
        args.__dict__.update(dataset.config.__dict__)
        pp = lambda x: pprint.PrettyPrinter().pprint(x)
        pp(args.__dict__)

        # Use CUDA or CPU
        USE_CUDA = torch.cuda.is_available()
        device = torch.device("cuda" if USE_CUDA else "cpu")

        # Init proxy
        m = DMN(args, dataset.idx2vec, args.set_num).to(device)
        # m.load_checkpoint()
        model_proxy = ModelProxy(m, dataset)
        print("model loaded successful")
    except Exception as e:
        print("model loaded failed")
        print("exception:")
        print(e)

if __name__ == "__main__":
    print("model loading ...")
    init_model()

    lines = [
        "Fred picked up the football in the hall.",
        "Fred gave the football to Jeff.",
        "Where is the football?"
    ]

    if model_proxy:
        model_proxy.predict(lines)
    # app.run(debug=True, host="0.0.0.0")
