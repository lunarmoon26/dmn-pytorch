from flask import Flask, request, jsonify
app = Flask(__name__)

@app.route("/")
def home():
    return "Server is running"

@app.route('/start')
def start():
    s_id = "new_session_id" # TODO: generate new session id
    return jsonify(id=s_id)

@app.route('/event', methods=['POST'])
def update_event():
    success = False
    s_id = request.form['id']
    fact = request.form['event']
    try:
        # TODO: append fact of s_id to the list
        success = True
    except ValueError as e:
        print(e)
    return jsonify(success=success)

@app.route('/answer', methods=['POST'])
def get_answer():
    success = False
    s_id = request.form['id']
    q = request.form['question']
    try:
        ans = "answer" # TODO: trigger the eval() and get the latest answer
        success = True
    except ValueError as e:
        print(e)
    return jsonify(answer=ans, success=success)




