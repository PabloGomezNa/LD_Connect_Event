# app.py

from flask import Flask
from routes.github_routes import github_bp
from routes.taiga_routes import taiga_bp
# ... import other routes as needed

def create_app():
    app = Flask(__name__)
    # If you have any config to set, do app.config["SOME_KEY"] = value here

    # Register your blueprint routes
    app.register_blueprint(github_bp)
    app.register_blueprint(taiga_bp)
    # ...
    return app

if __name__ == "__main__":
    app = create_app()
    # Typically you set host='0.0.0.0' so it’s externally accessible if needed
    app.run(debug=True, host="127.0.0.1", port=5000)
