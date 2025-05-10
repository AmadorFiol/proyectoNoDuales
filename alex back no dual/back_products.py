from flask import Flask, jsonify, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///BibliotecaCapitan.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Producto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    categoria = db.Column(db.String(50), nullable=True)
    nombre = db.Column(db.String(50), nullable=True)
    precio = db.Column(db.Integer, nullable=True)
    imagen = db.Column(db.String(50), nullable=True)

@app.route('/add_producto', methods=['GET', 'POST'])
def add_producto():
    if request.method == 'POST':
        id = request.form.get('id')
        nombre = request.form.get('nombre')
        categoria = request.form.get('categoria')            
        precio = request.form.get('precio')
        imagen = request.form.get('imagen')

        new_producto = Producto(
            id=id,
            categoria=categoria,
            nombre=nombre,
            precio=precio,
            imagen=imagen,
        )

        db.session.add(new_producto)
        db.session.commit()
        return redirect(url_for('add_producto.html'))
    return render_template('add_producto.html')


if __name__ == '__main__':
    app.run(debug=True)
