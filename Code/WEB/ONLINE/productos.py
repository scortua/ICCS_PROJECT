from flask import Flask, jsonify
import MySQLdb

app = Flask(__name__)

# Configuración de la base de datos (igual que en tu script)
db_config = {
    "host": "localhost",
    "user": "RPI4",
    "passwd": "raspberry4",
    "db": "Invernadero"
}

def get_db_connection():
    return MySQLdb.connect(**db_config)

@app.route('/productos', methods=['GET'])
def get_productos():
    db = get_db_connection()
    cursor = db.cursor(MySQLdb.cursors.DictCursor)  # Para obtener dicts
    cursor.execute("SELECT * FROM productos")  # Cambia 'productos' por tu tabla real
    productos = cursor.fetchall()
    cursor.close()
    db.close()
    return jsonify(productos)

if __name__ == '__main__':
    app.run(host='192.168.14.215', port=8000, debug=True)