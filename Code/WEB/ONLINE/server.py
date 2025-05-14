from flask import Flask, jsonify, request
from flask_cors import CORS
import MySQLdb

app = Flask(__name__)
CORS(app)  # Habilitar CORS para todas las rutas

# ConfiguraciÃ³n de la base de datos (igual que en tu script)
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

@app.route('/transacciones', methods=['POST'])
def registrar_compra():
    data = request.get_json()
    comprador = data.get('comprador')
    cantidad = data.get('cantidad')
    vendedor = data.get('vendedor')
    hash_bloque = data.get('hash')
    producto = data.get('producto')
    db = get_db_connection()
    cursor = db.cursor()
    cursor.execute("""
        INSERT INTO transacciones (id, comprador, cantidad, vendedor, hash, producto)
        VALUES (NULL, %s, %s, %s, %s, %s)
    """, (comprador, cantidad, vendedor, hash_bloque, producto))
    db.commit()
    cursor.close()
    db.close()
    return jsonify({'status': 'ok', 'msg': 'Compra registrada'})

if __name__ == '__main__':
    app.run(host='192.168.14.49', port=8000, debug=True)