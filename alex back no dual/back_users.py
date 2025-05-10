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

# Funcion añadir/registrar usuario
@app.route('/signup', methods=['GET', 'POST'])
def add_user():
    if request.method == 'POST':
        id = request.form.get('id')
        fecha_nacimiento_str = request.form.get('fecha_nacimiento')
        nombre = request.form.get('nombre')
        apellidos = request.form.get('apellidos')            
        pais = request.form.get('pais')
        gmail = request.form.get('gmail')

        # Convertir string a objeto date
        fecha_nacimiento = None
        if fecha_nacimiento_str:
            try:
                fecha_nacimiento = datetime.strptime(fecha_nacimiento_str, "%Y-%m-%d").date()
            except ValueError:
                return "Formato de fecha no válido", 400

        new_user = User(
            id=id,
            fecha_nacimiento=fecha_nacimiento,
            nombre=nombre,
            apellidos=apellidos,
            pais=pais,
            gmail=gmail
        )
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login_user'))
    return render_template('sesion.html')

# Funcion iniciar sesion de usuario ya existente
@app.route('/login', methods=['GET', 'POST'])
def login_user():
    if request.method == "POST":
        gmail = request.form.get('gmail')
        user = User.query.filter_by(gmail=gmail).first()
        if user:
            return redirect(url_for('user_profile', user_id=user.id)) 
        else:
            return render_template('user_profile_failed.html')
    return render_template('sesion.html')

# Perfil de usuario
@app.route('/user/<int:user_id>')
def user_profile(user_id):
    user = User.query.get(user_id)
    if user:
        return render_template('user_profile.html', user=user)
    else:
        return render_template('user_profile_failed.html')

if __name__ == '__main__':
    app.run(debug=True)
