from flask import Blueprint, jsonify, request, url_for
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.certificate_service import check_topic_complete, issue_certificate

cert_bp = Blueprint('certificate', __name__)

@cert_bp.route('/certificate/status', methods=['GET'])
@jwt_required()
def certificate_status():
    user_id  = get_jwt_identity()
    topic_id = request.args.get('topic_id', type=int)
    if topic_id is None:
        return jsonify({'error': 'Missing topic_id'}), 400

    complete = check_topic_complete(user_id, topic_id)
    return jsonify({'complete': complete}), 200

@cert_bp.route('/certificate/issue', methods=['POST'])
@jwt_required()
def issue_certificate_route():
    user_id  = get_jwt_identity()
    data      = request.get_json() or {}
    topic_id  = data.get('topic_id')
    if topic_id is None:
        return jsonify({'error': 'Missing topic_id'}), 400

    if not check_topic_complete(user_id, topic_id):
        return jsonify({'error': 'Not complete yet'}), 400

    cert    = issue_certificate(user_id, topic_id)
    pdf_url = url_for('static', filename=f"certs/{cert.pdf_path}", _external=True)
    return jsonify({'url': pdf_url}), 200
