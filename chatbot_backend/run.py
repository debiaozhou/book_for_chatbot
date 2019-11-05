from flask import Flask, request
import json
from bot8 import Chatbot_Model


app = Flask(__name__)


@app.route('/ask', methods=['GET', 'POST'])
def ask():
    parameter = request.json
    question = parameter['question']

    if not question:
        return_message = {'ErrorCode': '001', 'ErrorMsg': '提问为空！'}
    else:
        my_model = Chatbot_Model()
        answer = my_model.predict(question)
        return_message = {'answer': answer}

    return json.dumps(return_message)