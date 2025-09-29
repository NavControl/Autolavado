import mysql.connector
# Configuración de la conexión a MySQL

# PRODUCCIÓN
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'autolavado'
}

# Función para obtener una conexión a la base de datos
def get_db_connection():
    return mysql.connector.connect(
        host=DB_CONFIG['host'],
        user=DB_CONFIG['user'],
        password=DB_CONFIG['password'],
        database=DB_CONFIG['database']
    )
