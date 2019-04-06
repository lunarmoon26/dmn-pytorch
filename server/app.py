"""
Reference:
https://www.kdnuggets.com/2019/01/build-api-machine-learning-model-using-flask.html
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import numpy as np
import nltk
import torch
import argparse
import pickle
import pprint
from model.dataset import Dataset, Config
from torch.autograd import Variable

from model.model import DMN

app = Flask(__name__)
CORS(app)


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


def load_model():
    try:
        args = get_model_args()
        dataset = pickle.load(open(args.data_path, 'rb'))

        dataset.config.__dict__.update(args.__dict__)
        args.__dict__.update(dataset.config.__dict__)
        pp = lambda x: pprint.PrettyPrinter().pprint(x)
        pp(args.__dict__)

        # USE_CUDA = torch.cuda.is_available()
        USE_CUDA = False
        device = torch.device("cuda" if USE_CUDA else "cpu")

        m = DMN(args, dataset.idx2vec, args.set_num).to(device)
        m.load_checkpoint()
        m.eval()

        print("model loaded successful")

        return m
    except Exception as e:
        print("model loaded failed")
        print("exception:")
        print(e)
        return None


def get_model_args():
    argparser = argparse.ArgumentParser()
    # run settings
    argparser.add_argument('--data_path', type=str, default='../model/data/babi(tmp).pkl')
    argparser.add_argument('--model_name', type=str, default='m')
    argparser.add_argument('--checkpoint_dir', type=str, default='../model/results/')
    argparser.add_argument('--batch_size', type=int, default=32)
    argparser.add_argument('--epoch', type=int, default=100)
    argparser.add_argument('--train', type=int, default=0)
    argparser.add_argument('--valid', type=int, default=0)
    argparser.add_argument('--test', type=int, default=1)
    argparser.add_argument('--early_stop', type=int, default=0)
    argparser.add_argument('--resume', action='store_true', default=False)
    argparser.add_argument('--save', action='store_true', default=False)
    argparser.add_argument('--print_step', type=float, default=128)

    # model hyperparameters
    argparser.add_argument('--lr', type=float, default=0.0003)
    argparser.add_argument('--lr_decay', type=float, default=1.0)
    argparser.add_argument('--wd', type=float, default=0)
    argparser.add_argument('--grad_max_norm', type=int, default=5)
    argparser.add_argument('--s_rnn_hdim', type=int, default=100)
    argparser.add_argument('--s_rnn_ln', type=int, default=1)
    argparser.add_argument('--s_rnn_dr', type=float, default=0.0)
    argparser.add_argument('--q_rnn_hdim', type=int, default=100)
    argparser.add_argument('--q_rnn_ln', type=int, default=1)
    argparser.add_argument('--q_rnn_dr', type=float, default=0.0)
    argparser.add_argument('--e_cell_hdim', type=int, default=100)
    argparser.add_argument('--m_cell_hdim', type=int, default=100)
    argparser.add_argument('--a_cell_hdim', type=int, default=100)
    argparser.add_argument('--word_dr', type=float, default=0.2)
    argparser.add_argument('--g1_dim', type=int, default=500)
    argparser.add_argument('--max_episode', type=int, default=10)
    argparser.add_argument('--beta_cnt', type=int, default=10)
    argparser.add_argument('--set_num', type=int, default=1)
    argparser.add_argument('--max_alen', type=int, default=2)
    args = argparser.parse_args()

    return args


def map_dict(key_list, dictionary):
    output = []
    for key in key_list:
        # assert key in dictionary
        if key in dictionary:
            output.append(dictionary[key])
    return output


if __name__ == "__main__":
    print("model loading ...")
    model = load_model()

    stories = [
        ["Fred picked up the football there"],
        ["Fred gave the football to Jeff"]
    ]

    questions = [
        ["What did Fred give to Jeff"]
    ]

    wrap_tensor = lambda x: torch.LongTensor(np.array(x))
    wrap_var = lambda x: Variable(wrap_tensor(x))
    stories = wrap_var(stories)
    questions = wrap_var(questions)

    s_lens = wrap_tensor(6)
    q_lens = wrap_tensor(6)
    e_lens = wrap_tensor(6)

    x, y = model(stories, questions, s_lens, q_lens, e_lens)

    input_dict = {
        "dummy_id": ["data", "question"]
    }
    app.run(debug=True, host="0.0.0.0")
