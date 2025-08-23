from app import app

if __name__ == '__main__':
    # For development only
    app.run(host='0.0.0.0', port=5000, debug=True)
