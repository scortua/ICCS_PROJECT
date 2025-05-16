from telegram.ext import Application, ContextTypes, MessageHandler, filters, ConversationHandler, CommandHandler
from telegram import Update
import mysql.connector
from datetime import datetime

Token = "7973624993:AAEFZ7X9hcCLuzaJLPg_bMxzK9HMu-nBg1M"

# Configuración de la base de datos
db_config = {
    "host": "localhost",
    "user": "RPI4",
    "password": "raspberry4",
    "database": "Invernadero"
}

tablas = ["DHT22", "LEDS", "MQ_135", "WATER_PUMP", "YL"]

# Estados para la conversación de agregar producto
NOMBRE, CANTIDAD, DISPONIBILIDAD, PROPIETARIO = range(4)

def format_row(tabla, row):
    """Formatea una fila de datos según la tabla"""
    if tabla == "DHT22":
        return f"ID: {row[0]}, Temperatura: {row[1]}°C, Humedad: {row[2]}%, Fecha: {row[3]}"
    elif tabla == "LEDS":
        return f"ID: {row[0]}, Estado: {'Encendido' if row[1] else 'Apagado'}, Fecha: {row[2]}"
    elif tabla == "MQ_135":
        return f"ID: {row[0]}, CO2: {row[1]} ppm, Fecha: {row[2]}"
    elif tabla == "WATER_PUMP":
        return f"ID: {row[0]}, Estado: {'Encendido' if row[1] else 'Apagado'}, Fecha: {row[2]}"
    elif tabla == "YL":
        return f"ID: {row[0]}, Humedad del suelo: {row[1]}%, Fecha: {row[2]}"
    elif tabla == "PRODUCTOS":
        return f"ID: {row[0]}, Producto: {row[1]}, Cantidad: {row[2]}, Disponible: {'Sí' if row[3] else 'No'}, Propietario: {row[4]}, Fecha: {row[5]}"
    return str(row)

def get_ultimos_datos():
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    msg = "📊 *ÚLTIMO DATO DE CADA SENSOR* 📊\n"
    for tabla in tablas:
        cursor.execute(f"SELECT * FROM {tabla} ORDER BY id DESC LIMIT 1")
        row = cursor.fetchone()
        msg += f"\n📌 *{tabla}*:\n"
        if row:
            msg += f"  {format_row(tabla, row)}\n"
        else:
            msg += f"  No hay datos.\n"
    # Agregar productos si existe la tabla
    try:
        cursor.execute(f"SELECT * FROM PRODUCTOS ORDER BY id DESC LIMIT 5")
        rows = cursor.fetchall()
        msg += f"\n📦 *PRODUCTOS RECIENTES*:\n"
        if rows:
            for row in rows:
                msg += f"  {format_row('PRODUCTOS', row)}\n"
        else:
            msg += "  No hay productos registrados.\n"
    except:
        msg += "\n📦 *PRODUCTOS*: Tabla no disponible.\n"
    cursor.close()
    conn.close()
    return msg

def get_datos_hoy():
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    msg = "📊 *ÚLTIMOS 10 DATOS DE CADA SENSOR* 📊\n"
    for tabla in tablas:
        cursor.execute(f"SELECT * FROM {tabla} ORDER BY id DESC LIMIT 10")
        rows = cursor.fetchall()
        msg += f"\n📌 *{tabla}*:\n"
        if rows:
            for row in rows:
                msg += f"  {format_row(tabla, row)}\n"
        else:
            msg += "  No hay datos.\n"
    cursor.close()
    conn.close()
    return msg

def crear_tabla_productos_si_no_existe():
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    try:
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS PRODUCTOS (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nombre VARCHAR(100) NOT NULL,
            cantidad INT NOT NULL,
            disponibilidad BOOLEAN NOT NULL,
            propietario VARCHAR(100) NOT NULL,
            fecha DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """)
        conn.commit()
    except Exception as e:
        print(f"Error al crear tabla PRODUCTOS: {e}")
    finally:
        cursor.close()
        conn.close()

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip().lower()
    if text == ".":
        await update.message.reply_text(
            "📋 *Comandos disponibles*:\n"
            "- *datos hoy*: Muestra los últimos 10 registros de cada sensor\n"
            "- *ultimos datos*: Muestra el último registro de cada sensor\n"
            "- *agregar producto*: Inicia el proceso para registrar un nuevo producto\n"
            "- *finalizar*: Termina la conversación con el bot"
        )
    elif text == "datos hoy":
        await update.message.reply_text(get_datos_hoy())
    elif text == "ultimos datos":
        await update.message.reply_text(get_ultimos_datos())
    elif text == "agregar producto":
        await update.message.reply_text("Por favor, ingresa el nombre del producto:")
        return NOMBRE
    elif text == "finalizar":
        await update.message.reply_text("¡Hasta luego! Gracias por usar el bot.")
    else:
        await update.message.reply_text("Comando no reconocido. Escribe '.' para ver los comandos disponibles.")
    return ConversationHandler.END

async def nombre_producto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['nombre'] = update.message.text
    await update.message.reply_text("Ahora, ingresa la cantidad:")
    return CANTIDAD

async def cantidad_producto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        cantidad = int(update.message.text)
        context.user_data['cantidad'] = cantidad
        await update.message.reply_text("¿Está disponible? (si/no):")
        return DISPONIBILIDAD
    except ValueError:
        await update.message.reply_text("Por favor, ingresa un número válido para la cantidad:")
        return CANTIDAD

async def disponibilidad_producto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    respuesta = update.message.text.strip().lower()
    if respuesta in ["si", "sí", "yes", "1", "true"]:
        context.user_data['disponibilidad'] = True
    else:
        context.user_data['disponibilidad'] = False
    await update.message.reply_text("Por último, ¿quién es el propietario?:")
    return PROPIETARIO

async def propietario_producto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['propietario'] = update.message.text
    
    # Guardar en la base de datos
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO PRODUCTOS (nombre, cantidad, disponibilidad, propietario) VALUES (%s, %s, %s, %s)",
            (context.user_data['nombre'], context.user_data['cantidad'], 
             context.user_data['disponibilidad'], context.user_data['propietario'])
        )
        conn.commit()
        cursor.close()
        conn.close()
        
        await update.message.reply_text(
            f"✅ Producto agregado correctamente:\n"
            f"- Nombre: {context.user_data['nombre']}\n"
            f"- Cantidad: {context.user_data['cantidad']}\n"
            f"- Disponible: {'Sí' if context.user_data['disponibilidad'] else 'No'}\n"
            f"- Propietario: {context.user_data['propietario']}"
        )
    except Exception as e:
        await update.message.reply_text(f"❌ Error al guardar el producto: {e}")
    
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Operación cancelada.")
    return ConversationHandler.END

def main():
    crear_tabla_productos_si_no_existe()
    
    bot = Application.builder().token(Token).build()
    
    # Manejador de conversación para agregar productos
    conv_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex(r'^agregar producto$'), echo)],
        states={
            NOMBRE: [MessageHandler(filters.TEXT & ~filters.COMMAND, nombre_producto)],
            CANTIDAD: [MessageHandler(filters.TEXT & ~filters.COMMAND, cantidad_producto)],
            DISPONIBILIDAD: [MessageHandler(filters.TEXT & ~filters.COMMAND, disponibilidad_producto)],
            PROPIETARIO: [MessageHandler(filters.TEXT & ~filters.COMMAND, propietario_producto)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    
    bot.add_handler(conv_handler)
    bot.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
    bot.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()