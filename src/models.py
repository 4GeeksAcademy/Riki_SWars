# 👇👇👇 ✅ Importamos las herramientas que necesitamos
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import String, Boolean, Column, Integer, ForeignKey, Table, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship

# 👇👇👇 ✅ Esto es para arrancar SQLAlchemy. Esta variable es quien "maneja" todas nuestras tablas en la base de datos.
db = SQLAlchemy()

# 👇👇👇 ✅ Creamos la tabla de Usuarios
class User(db.Model):
    __tablename__ = 'user'  # Nombre de la tabla

    # 👇👇👇 ✅ Estas son las columnas que tiene nuestra tabla de usuarios
    id: Mapped[int] = mapped_column(primary_key=True)  # ID único para cada usuario
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)  # Correo electrónico (único y obligatorio)
    password: Mapped[str] = mapped_column(String(80), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean(), nullable=False)  # Estado del usuario (activo o inactivo)

    # Relación con la tabla Favoritos (un usuario puede tener muchos favoritos)
    favorite_planets: Mapped[list["FavoritePlanet"]] = relationship("FavoritePlanet", back_populates="user")
    favorite_person: Mapped[list["FavoritePerson"]] = relationship("FavoritePerson", back_populates="user")
    favorite_vehicles: Mapped[list["FavoriteVehicle"]] = relationship("FavoriteVehicle", back_populates="user")

    # Método para serializar el objeto (convertirlo a JSON)
    def serialize(self):
        return {
            "id": self.id,
            "email": self.email,
            "is_active": self.is_active,
            # No serializamos la contraseña por seguridad
        }

# 👇👇👇 ✅ Esta es la tabla de Planetas
class Planet(db.Model):
    __tablename__ = 'planet'  # Nombre de la tabla

    # 👇👇👇 ✅ Estas son las columnas que tiene nuestra tabla de planetas
    id: Mapped[int] = mapped_column(primary_key=True)  # ID único para cada planeta
    name: Mapped[str] = mapped_column(String(120), nullable=False)  
    climate: Mapped[str] = mapped_column(String(80), nullable=False)
    gravity: Mapped[str] = mapped_column(String(80), nullable=False)

    # Relación inversa: un planeta conoce a los personajes que lo tienen como mundo de origen.
    person: Mapped[list["Person"]] = relationship("Person", back_populates="home_world")
    
    # Relación: un planeta puede ser marcado como favorito por muchos usuarios.
    favorite_planets: Mapped[list["FavoritePlanet"]] = relationship("FavoritePlanet", back_populates="planet", cascade='all, delete-orphan')

    # Método para serializar el objeto
    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "climate": self.climate,
            "gravity": self.gravity,
        }

# 👇👇👇 ✅ Esta es la tabla de Personajes
class Person(db.Model):
    __tablename__ = 'person'  # Nombre de la tabla

    # 👇👇👇 ✅ Estas son las columnas que tiene nuestra tabla de Person
    id: Mapped[int] = mapped_column(primary_key=True)  # ID único para cada personaje
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    skin_color: Mapped[str] = mapped_column(String(80), nullable=False)
    home_world_id: Mapped[int] = mapped_column(db.ForeignKey("planet.id"))

    # Relación: cada personaje tiene un planeta de origen.
    home_world: Mapped["Planet"] = relationship("Planet", back_populates="person")
    
    # Relación con la tabla de favoritos específicos de personajes.
    favorite_person: Mapped[list["FavoritePerson"]] = relationship("FavoritePerson", back_populates="person", cascade='all, delete-orphan')

    # Método para serializar el objeto
    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "skin_color": self.skin_color,
        }

# 👇👇👇 ✅ Esta es la tabla de Vehículos
class Vehicles(db.Model):
    __tablename__ = 'vehicles'  # Nombre de la tabla

    # 👇👇👇 ✅ Estas son las columnas que tiene nuestra tabla de Vehicles
    id: Mapped[int] = mapped_column(primary_key=True)  # ID único para cada vehículo
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    crew: Mapped[str] = mapped_column(String(80), nullable=False) 
    consumables: Mapped[str] = mapped_column(String(80), nullable=False) 

    # Relación con la tabla de favoritos específicos de vehículos.
    favorite_vehicles: Mapped[list["FavoriteVehicle"]] = relationship("FavoriteVehicle", back_populates="vehicle", cascade='all, delete-orphan')

    # Método para serializar el objeto
    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "crew": self.crew,
            "consumables": self.consumables,
        }

# 👇👇👇 ✅ TABLA DE FAVORITOS DE PLANETAS

class FavoritePlanet(db.Model):
    __tablename__ = 'favorite_planet'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    planet_id: Mapped[int] = mapped_column(ForeignKey("planet.id"))
    
    user: Mapped["User"] = relationship("User", back_populates="favorite_planets")
    planet: Mapped["Planet"] = relationship("Planet", back_populates="favorite_planets")
    
    def serialize(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "planet_id": self.planet_id,
        }


# 👇👇👇 ✅ TABLA DE FAVORITOS DE PERSONAJES

class FavoritePerson(db.Model):
    __tablename__ = 'favorite_person'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    person_id: Mapped[int] = mapped_column(ForeignKey("person.id"))
    
    user: Mapped["User"] = relationship("User", back_populates="favorite_person")
    # Nota: aquí usamos "person" para indicar el personaje favorito
    person: Mapped["Person"] = relationship("Person", back_populates="favorite_person")
    
    def serialize(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "person_id": self.person_id,
        }


# 👇👇👇 ✅ TABLA DE FAVORITOS DE VEHÍCULOS
class FavoriteVehicle(db.Model):
    __tablename__ = 'favorite_vehicle'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    vehicle_id: Mapped[int] = mapped_column(ForeignKey("vehicles.id"))

    user: Mapped["User"] = relationship("User", back_populates="favorite_vehicles")
    vehicle: Mapped["Vehicles"] = relationship("Vehicles", back_populates="favorite_vehicles")
    
    def serialize(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "vehicle_id": self.vehicle_id,
        }