import configparser
from sqlalchemy import create_engine

# aca se lee el archivo de configuracion para la conexion a la base de datos
config = configparser.ConfigParser()
config.read('config.txt')

engine = create_engine(config.get('database', 'con'))