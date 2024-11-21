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
from models import db, Users,Planets,Favorites,Characters

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

#### Endpoints ####


#### Characters ####

# [GET] /characters - Obtener todos los personajes

@app.route('/characters', methods=['GET'])
def get_all_characters():
    characters = Characters.query.all()  # Obtiene todos los registros de la tabla Characters
    
    # Convertir los resultados a un formato JSON
    characters_list = []
    for character in characters:
        characters_list.append({
            'character_id': character.character_id,
            'name': character.name,
            'species': character.species,
            'homeworld': character.homeworld,
            'gender': character.gender
        })
    
    return jsonify(characters_list), 200

# [GET] /character/<int:character_id> - Obtener la información de un personaje por ID

@app.route('/character/<int:character_id>', methods=['GET'])
def get_character(character_id):

    character = Characters.query.filter_by(character_id=character_id).first()  # Devuelve el primer resultado o None si no se encuentra
    
    if character is None:
        return jsonify({"message": "Character not found"}), 404

    character_data = {
        'character_id': character.character_id,
        'name': character.name,
        'species': character.species,
        'homeworld': character.homeworld,
        'gender': character.gender
    }

    return jsonify(character_data), 200

# [POST] /character - Agregar un personaje

@app.route('/character', methods=['POST'])
def add_character():
    data = request.get_json()

    if 'name' not in data or 'species' not in data or 'homeworld' not in data:
        return jsonify({"error": "Missing required fields"}), 400

    new_character = Characters(
        name=data['name'],
        species=data['species'],
        homeworld=data['homeworld'],
        gender=data.get('gender', None)
    )

    db.session.add(new_character)
    db.session.commit()

    return jsonify({
        "message": "Character added successfully",
        "character_id": new_character.character_id,
        "name": new_character.name
    }), 201

#  [PUT] /character/<int:character_id> - Modificar personaje


@app.route('/character/<int:character_id>', methods=['PUT'])
def update_character(character_id):

    data = request.get_json()

    character = Characters.query.get(character_id)
    
    if not character:
        return jsonify({"error": "Character not found"}), 404

    character.name = data.get('name', character.name)
    character.species = data.get('species', character.species)
    character.homeworld = data.get('homeworld', character.homeworld)
    character.gender = data.get('gender', character.gender)

    db.session.commit()

    return jsonify({
        "message": "Character updated successfully",
        "character_id": character.character_id,
        "name": character.name
    }), 200

#  [DELETE] /character/<int:character_id> - Eliminar personaje


@app.route('/character/<int:character_id>', methods=['DELETE'])
def delete_character(character_id):

    character = Characters.query.get(character_id)
    
    if not character:
        return jsonify({"error": "Character not found"}), 404

    db.session.delete(character)
    db.session.commit()

    return jsonify({
        "message": "Character deleted successfully",
        "character_id": character_id
    }), 200


#### Fin Characters ####


#### Planets ####

# [GET] /planets - Obtener todos los planetas

@app.route('/planets', methods=['GET'])
def get_all_planets():
    planets = Planets.query.all() 
    
    planets_list = []
    for planet in planets:
        planets_list.append({
            'planet_id': planet.planet_id,
            'name': planet.name,
            'climate': planet.climate,
            'terrain': planet.terrain,
            'population': planet.population
        })
    
    return jsonify(planets_list), 200


# [GET] /planet/<int:planet_id> - Obtener la información de un planeta por ID

@app.route('/planet/<int:planet_id>', methods=['GET'])
def get_planet(planet_id):

    planet = Planets.query.filter_by(planet_id=planet_id).first()
    
    if planet is None:
        return jsonify({"message": "Planet not found"}), 404

    planet_data = {
        'planet_id': planet.planet_id,
        'name': planet.name,
        'climate': planet.climate,
        'terrain': planet.terrain,
        'population': planet.population
    }

    return jsonify(planet_data), 200

# [POST] /planet - Agregar un planeta

@app.route('/planet', methods=['POST'])
def add_planet():
    data = request.get_json()

    if 'name' not in data or 'climate' not in data or 'terrain' not in data:
        return jsonify({"error": "Missing required fields"}), 400

    new_planet = Planets(
        name=data['name'],
        climate=data['climate'],
        terrain=data['terrain'],
        population=data.get('population', None)
    )

    db.session.add(new_planet)
    db.session.commit()

    return jsonify({
        "message": "Planet added successfully",
        "planet_id": new_planet.planet_id,
        "name": new_planet.name
    }), 201

#  [PUT] /planet/<int:planet_id> - Modificar planeta de la BD

@app.route('/planet/<int:planet_id>', methods=['PUT'])
def update_planet(planet_id):

    data = request.get_json()

    planet = Planets.query.get(planet_id)
    
    if not planet:
        return jsonify({"error": "Planet not found"}), 404

    planet.name = data.get('name', planet.name)
    planet.climate = data.get('climate', planet.climate)
    planet.terrain = data.get('terrain', planet.terrain)
    planet.population = data.get('population', planet.population)

    db.session.commit()

    return jsonify({
        "message": "Planet updated successfully",
        "planet_id": planet.planet_id,
        "name": planet.name
    }), 200


#  [DELETE] /planet/<int:planet_id> - Eliminar planeta de la bd

@app.route('/planet/<int:planet_id>', methods=['DELETE'])
def delete_planet(planet_id):

    planet = Planets.query.get(planet_id)
    
    if not planet:
        return jsonify({"error": "Planet not found"}), 404

    db.session.delete(planet)
    db.session.commit()

    return jsonify({
        "message": "Planet deleted successfully",
        "planet_id": planet_id
    }), 200


#### Fin Planets ####

#### Users ####

# [GET] /users - Listar todos los usuarios

@app.route('/users', methods=['GET'])
def get_all_users():
    users = Users.query.all() 
    users_data = []
    for user in users:
        users_data.append({
            'user_id': user.user_id,
            'email': user.email,
            'username': user.username,
            'user_creation_date': user.user_creation_date
        })
    return jsonify(users_data), 200

# [GET] /users/favorites - Listar todos los favoritos del usuario actual

@app.route('/users/favorites', methods=['GET'])
def get_user_favorites():
    # Usamos un user_id hardcodeado para simular el proceso de autenticación
    current_user_id = 1  # Esto se remplaza por la autenticación del próximo ejercicio.
    
    # Obtener los favoritos del usuario
    favorites = Favorites.query.filter_by(user_id=current_user_id).all()
    favorites_data = []

    for favorite in favorites:
        if favorite.favorite_type == 'planet':
            planet = Planets.query.get(favorite.favorite_id_ref)
            favorites_data.append({
                'favorite_type': favorite.favorite_type,
                'planet_id': planet.planet_id,
                'name': planet.name
            })
        elif favorite.favorite_type == 'character':
            character = Characters.query.get(favorite.favorite_id_ref)
            favorites_data.append({
                'favorite_type': favorite.favorite_type,
                'character_id': character.character_id,
                'name': character.name
            })
    
    return jsonify(favorites_data), 200

# [POST] /favorite/planet/<int:planet_id> - Agregar un nuevo planeta favorito

@app.route('/favorite/planet/<int:planet_id>', methods=['POST'])
def add_favorite_planet(planet_id):
    # Usamos un user_id hardcodeado para simular el proceso de autenticación
    current_user_id = 1  # Esto se remplaza por la autenticación del próximo ejercicio.
    
    # Verificar si el planeta existe en la base de datos
    planet = Planets.query.get(planet_id)
    if planet is None:
        return jsonify({"error": "Planet not found"}), 404
    
    # Crear un nuevo registro de favorito
    new_favorite = Favorites(user_id=current_user_id, favorite_type="planet", favorite_id_ref=planet_id)
    
    # Agregar el nuevo favorito a la base de datos
    db.session.add(new_favorite)
    db.session.commit()
    
    return jsonify({
        "message": "Planet added to favorites",
        "planet_id": planet_id,
        "planet_name": planet.name
    }), 201

# [POST] /favorite/character/<int:character_id>' - Agregar un nuevo personaje favorito

@app.route('/favorite/character/<int:character_id>', methods=['POST'])
def add_favorite_character(character_id):
    # Usamos un user_id hardcodeado para simular el proceso de autenticación
    current_user_id = 1  # Esto se remplaza por la autenticación del próximo ejercicio.
    
    character = Characters.query.get(character_id)
    if character is None:
        return jsonify({"error": "Character not found"}), 404
    
    new_favorite = Favorites(user_id=current_user_id, favorite_type="character", favorite_id_ref=character_id)
    
    db.session.add(new_favorite)
    db.session.commit()
    
    return jsonify({
        "message": "Character added to favorites",
        "character_id": character_id,
        "character_name": character.name
    }), 201

# [DELETE] /favorite/planet/<int:planet_id> - Eliminar un planeta favorito

@app.route('/favorite/planet/<int:planet_id>', methods=['DELETE'])
def delete_favorite_planet(planet_id):

    current_user_id = 1  
    
    favorite = Favorites.query.filter_by(user_id=current_user_id, favorite_type="planet", favorite_id_ref=planet_id).first()
    
    if not favorite:
        return jsonify({"error": "Favorite planet not found"}), 404
    
    db.session.delete(favorite)
    db.session.commit()
    
    return jsonify({
        "message": "Planet removed from favorites",
        "planet_id": planet_id
    }), 200


# [DELETE] /favorite/character/<int:character_id> - Eliminar un character favorito

@app.route('/favorite/character/<int:character_id>', methods=['DELETE'])
def delete_favorite_character(character_id):

    current_user_id = 1 
    
    favorite = Favorites.query.filter_by(user_id=current_user_id, favorite_type="character", favorite_id_ref=character_id).first()
    
    if not favorite:
        return jsonify({"error": "Favorite character not found"}), 404
    
    db.session.delete(favorite)
    db.session.commit()
    
    return jsonify({
        "message": "Character removed from favorites",
        "character_id": character_id
    }), 200


#### Fin Users  ####


# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
