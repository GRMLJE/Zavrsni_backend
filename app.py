import logging

from flask import Flask, jsonify
from flask_cors import CORS

from routes.admin import admin_bp
from routes.categories import categories_bp
from routes.cities import cities_bp
from routes.events import events_bp
from routes.neighborhoods import neighborhoods_bp
from routes.users import users_bp

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

app = Flask(__name__)
CORS(app)

app.register_blueprint(admin_bp)
app.register_blueprint(categories_bp)
app.register_blueprint(cities_bp)
app.register_blueprint(neighborhoods_bp)
app.register_blueprint(events_bp)
app.register_blueprint(users_bp)


@app.errorhandler(Exception)
def handle_exception(e):
    app.logger.error("Unhandled exception: %s", e, exc_info=True)
    return jsonify({"error": "Interna greška servera."}), 500


@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Resurs nije pronađen."}), 404


@app.errorhandler(405)
def method_not_allowed(e):
    return jsonify({"error": "Metoda nije dozvoljena."}), 405


if __name__ == "__main__":
    app.run(debug=True)
