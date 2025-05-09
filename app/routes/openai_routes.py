# app/routes/openai_routes.py

import os
from flask import Blueprint, request, jsonify
import openai

openai_bp = Blueprint('openai', __name__)
# print("OpenAI key:", os.getenv("OPENAI_API_KEY")) 
openai.api_key = os.getenv('OPENAI_API_KEY') 

@openai_bp.route('/chat', methods=['POST'])
def chat():
    """
    Nhận `messages` từ frontend, forward lên OpenAI Chat API,
    trả về `choices[0].message` nguyên vẹn.
    """
    data = request.get_json() or {}
    messages = data.get('messages')
    if not messages or not isinstance(messages, list):
        return jsonify({'error': 'Invalid messages payload'}), 400

    try:
        resp = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=0.2,
            max_tokens=500,
        )
        # gửi nguyên message.content về frontend
        return jsonify({ 'message': resp.choices[0].message }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
