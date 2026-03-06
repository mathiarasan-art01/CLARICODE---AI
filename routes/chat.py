from flask import Blueprint, request, jsonify
from llm_engine import call_ai

chat_bp = Blueprint("chat", __name__)

@chat_bp.route("/", methods=["POST"])
def chat():

    data = request.get_json()
    message = data.get("message")

    messages = [
        {
            "role": "system",
            "content": "You are a helpful AI tutor. Answer briefly and clearly."
        },
        {
            "role": "user",
            "content": message
        }
    ]

    response = call_ai(messages)

    return jsonify({"reply": response})