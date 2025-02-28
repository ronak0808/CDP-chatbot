from app import create_app

app = create_app()

if __name__ == '__main__':
    # Run the application with settings suitable for web-based environment
    app.run(
        host='0.0.0.0',  # Allow external access
        port=5001,       # Use different port since 5000 is in use
        debug=True
    )
