from flask import Flask
from logging.config import dictConfig

# Configure logging
dictConfig({
    'version': 1,
    'formatters': {
        'default': {
            'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
        }
    },
    'handlers': {
        'wsgi': {
            'class': 'logging.StreamHandler',
            'stream': 'ext://flask.logging.wsgi_errors_stream',
            'formatter': 'default'
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': 'app.log',
            'formatter': 'default'
        }
    },
    'root': {
        'level': 'INFO',
        'handlers': ['wsgi', 'file']
    }
})

def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__)
    
    # Configure app
    app.config.update(
        SECRET_KEY='dev-key-please-change-in-production',
        JSON_SORT_KEYS=False,
        MAX_CONTENT_LENGTH=16 * 1024 * 1024  # 16MB max-limit
    )

    # Register blueprints
    from app.routes import main_bp
    app.register_blueprint(main_bp)

    # Error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        """Handle 404 errors."""
        return jsonify({
            'error': 'Not Found',
            'message': 'The requested resource was not found on this server.'
        }), 404

    @app.errorhandler(500)
    def internal_error(error):
        """Handle 500 errors."""
        return jsonify({
            'error': 'Internal Server Error',
            'message': 'An unexpected error occurred. Please try again later.'
        }), 500

    @app.after_request
    def after_request(response):
        """Add security headers to response."""
        response.headers["X-Frame-Options"] = "SAMEORIGIN"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        return response

    return app

# Import jsonify here to avoid circular imports
from flask import jsonify
