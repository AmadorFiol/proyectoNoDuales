from flask import Flask, jsonify, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///BibliotecaCapitan.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fecha_nacimiento = db.Column(db.Date, nullable=True)
    nombre = db.Column(db.String(50), nullable=True)
    apellidos = db.Column(db.String(50), nullable=True)
    pais = db.Column(db.String(50), nullable=True)
    gmail = db.Column(db.String(50), nullable=True)
    
    
class Producto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    precio = db.Column(db.Float, nullable=False)
    imagen = db.Column(db.String(200), nullable=False)

@app.route('/')
def index():
    # ordenar = request.args.get("ordenar", "precio-desc")
    
    # productos = [
    #     {"nombre": "Producto A", "precio": 50},
    #     {"nombre": "Producto B", "precio": 30},
    #     {"nombre": "Producto C", "precio": 70}
    # ]

    # if ordenar == "precio-asc":
    #     productos.sort(key=lambda x: x["precio"])
    # elif ordenar == "precio-desc":
    #     productos.sort(key=lambda x: x["precio"], reverse=True)
    # elif ordenar == "nombre-az":
    #     productos.sort(key=lambda x: x["nombre"])

    return render_template("index.html")

@app.route('/signup', methods=['GET', 'POST'])
def add_user():
    if request.method == 'POST':
        id = request.form.get('id')
        fecha_nacimiento = request.form.get('fecha_nacimiento')
        nombre = request.form.get('nombre')
        apellidos = request.form.get('apellidos')            
        pais = request.form.get('pais')
        gmail = request.form.get('gmail')
        new_user = User(id=id, fecha_nacimiento=fecha_nacimiento, nombre=nombre, apellidos=apellidos, pais=pais, gmail=gmail)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('get_libros')) 
    return render_template('signup.html')

@app.route('/singin', methods=['GET', 'POST'])
def login_user():
    if request.method == "POST":
        gmail = request.form.get('gmail')
        user = User.query.filter_by(gmail=gmail).first()
        if user:
           #Logica sintaxis del user
            return redirect(url_for('user_profile', user_id=user.id)) 
        else:
            return 'Usuario no encontrado', 404
    return render_template('login.html') 

@app.route('/user/<int:user_id>')
def user_profile(user_id):
    user = User.query.get(user_id)
    if user:
        return jsonify({
            "id": user.id, 
            "Nombre": user.nombre, 
            "Apellidos": user.apellidos, 
            "Gmail": user.gmail, 
            "Pais": user.pais, 
            "Fecha_nacimiento": user.fecha_nacimiento.strftime("%Y-%m-%d")
        })
    else:
        return jsonify({"error": "Usuario no encontrado"}), 404

@app.route('/productos')
def productos():
    return render_template("productos.html")

if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.run(debug=True)