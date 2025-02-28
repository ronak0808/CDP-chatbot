from flask import Blueprint, render_template, request, jsonify
from app.chatbot import process_question
import logging

main_bp = Blueprint('main', __name__)
logger = logging.getLogger(__name__)

@main_bp.route('/')
def index():
    """Serve the main chatbot interface."""
    return render_template('index.html')

@main_bp.route('/api/chat', methods=['POST'])
def chat():
    """Handle chat API requests."""
    try:
        data = request.get_json()
        
        if not data or 'question' not in data:
            return jsonify({
                'error': 'Missing question parameter'
            }), 400

        question = data['question'].strip()
        
        if not question:
            return jsonify({
                'error': 'Question cannot be empty'
            }), 400

        # Process the question and get response
        response = process_question(question)
        
        return jsonify({
            'success': True,
            'response': response
        })

    except Exception as e:
        logger.error(f"Error processing chat request: {str(e)}")
        return jsonify({
            'error': 'An error occurred while processing your request'
        }), 500

@main_bp.route('/api/health')
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'service': 'cdp-chatbot'
    })
