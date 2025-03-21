"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Planet, Person, FavoritePlanet, FavoritePerson, FavoriteVehicle
#from models import Person
app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

# Endpoints para Person

# 👇👇👇 ✅ [GET] /person Listar todos los registros de person en la base de datos.
@app.route('/person', methods=['GET'])
def get_all_person():
    person_list = Person.query.all()
    return jsonify([person.serialize() for person in person_list]), 200

# 👇👇👇 ✅ [GET] /person/<int:person_id>: Muestra la información de un solo personaje según su id
@app.route('/person/<int:person_id>', methods=['GET'])
def get_one_person(person_id):
    person = Person.query.get(person_id)
    if not person:
        return jsonify({"error": "Personaje no encontrado"}), 404
    return jsonify(person.serialize()), 200


# Endpoints para Planets

# 👇👇👇 ✅ [GET] /planets: Listar todos los registros de planets
@app.route('/planets', methods=['GET'])
def get_all_planets():
    planet_list = Planet.query.all()
    return jsonify([planet.serialize() for planet in planet_list]), 200

# 👇👇👇 ✅ [GET] /planets/<int:planet_id>: Muestra la información de un solo planeta según su id
@app.route('/planets/<int:planet_id>', methods=['GET'])
def get_one_planet(planet_id):
    planet = Planet.query.get(planet_id)
    if not planet:
        return jsonify({"error": "Planeta no encontrado"}), 404
    return jsonify(planet.serialize()), 200

# Endpoints para Usuarios y Favoritos

# 👇👇👇 ✅ [GET] /users: Listar todos los usuarios del blog
@app.route('/users', methods=['GET'])
def get_all_users():
    users = User.query.all()
    return jsonify([user.serialize() for user in users]), 200

# 👇👇👇 ✅ [GET] /users/favorites: Listar todos los favoritos que pertenecen al usuario actual
@app.route('/users/favorites/<int:user_id>', methods=['GET'])
def get_user_favorites(user_id):
    favorite_planets = FavoritePlanet.query.filter_by(user_id=user_id).all()
    favorite_person = FavoritePerson.query.filter_by(user_id=user_id).all()
    return jsonify({
        "favorite_planets": [fav.serialize() for fav in favorite_planets],
        "favorite_person": [fav.serialize() for fav in favorite_person]
    }), 200

# 👇👇👇 ✅ [POST] /favorite/planet/<int:planet_id>: Añade un nuevo planet favorito al usuario actual
@app.route('/favorite/<int:user_id>/planet/<int:planet_id>', methods=['POST'])
def add_favorite_planet(user_id, planet_id):
    
    # Verificamos que el planeta exista
    planet = Planet.query.get(planet_id)
    if not planet:
        return jsonify({"error": "Planeta no encontrado"}), 404

    # Verificamos que el favorito no exista ya para este usuario y planeta
    existing_fav = FavoritePlanet.query.filter_by(user_id=user_id, planet_id=planet_id).first()
    if existing_fav:
        return jsonify({"error": "El planeta ya está en favoritos"}), 400

    new_fav = FavoritePlanet(user_id=user_id, planet_id=planet_id)
    db.session.add(new_fav)
    db.session.commit()
    return jsonify(new_fav.serialize()), 201

# 👇👇👇 ✅ [POST] /favorite/person/<int:person_id>: Añade un nuevo person favorito al usuario actual
@app.route('/favorite/<int:user_id>/person/<int:person_id>', methods=['POST'])
def add_favorite_person(user_id, person_id):
    
    # Verificamos que el personaje exista
    person = Person.query.get(person_id)
    if not person:
        return jsonify({"error": "Personaje no encontrado"}), 404

    # Verificamos que el favorito no exista ya para este usuario y personaje
    existing_fav = FavoritePerson.query.filter_by(user_id=user_id, person_id=person_id).first()
    if existing_fav:
        return jsonify({"error": "El personaje ya está en favoritos"}), 400

    new_fav = FavoritePerson(user_id=user_id, person_id=person_id)
    db.session.add(new_fav)
    db.session.commit()
    return jsonify(new_fav.serialize()), 201

# 👇👇👇 ✅ [DELETE] /favorite/planet/<int:planet_id>: Elimina un planet favorito con el id = planet_id para el usuario actual
@app.route('/favorite/<int:user_id>/planet/<int:planet_id>', methods=['DELETE'])
def delete_favorite_planet(user_id, planet_id):
    fav = FavoritePlanet.query.filter_by(user_id=user_id, planet_id=planet_id).first()
    if not fav:
        return jsonify({"error": "Favorito de planeta no encontrado"}), 404
    db.session.delete(fav)
    db.session.commit()
    return jsonify({"message": "Favorito de planeta eliminado correctamente"}), 200

# 👇👇👇 ✅ [DELETE] /favorite/person/<int:person_id>: Elimina un person favorito con el id = person_id para el usuario actual
@app.route('/favorite/<int:user_id>/person/<int:person_id>', methods=['DELETE'])
def delete_favorite_person(user_id, person_id):
    fav = FavoritePerson.query.filter_by(user_id=user_id, person_id=person_id).first()
    if not fav:
        return jsonify({"error": "Favorito de personaje no encontrado"}), 404
    db.session.delete(fav)
    db.session.commit()
    return jsonify({"message": "Favorito de personaje eliminado correctamente"}), 200
    


# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
