from flask import Flask, jsonify, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///electromarkt.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/img/productos'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Límite de 16 MB
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False)
    apellidos = db.Column(db.String(50), nullable=False)
    pais = db.Column(db.String(50), nullable=False)
    gmail = db.Column(db.String(50), nullable=False)
    password=db.Column(db.String(50),nullable=False)
    
    
class Producto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    precio = db.Column(db.Float, nullable=False)
    imagen = db.Column(db.String(200), nullable=False)
    categoria=db.Column(db.Integer, nullable=False)

class Categoria(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    nombre=db.Column(db.String(100), nullable=False)

class Carrito(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    idUser=db.Column(db.Integer)

class CarProd(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    idCarrito=db.Column(db.Integer, nullable=False)
    idProd=db.Column(db.Integer, nullable=False)
    cantidad=db.Column(db.Integer, nullable=False)

def allowed_file(filename):
    return '.' in filename and filename.split('.')[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/singup', methods=['GET', 'POST'])
def singup():
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        apellidos = request.form.get('apellidos')            
        pais = request.form.get('pais')
        gmail = request.form.get('gmail')
        password=request.form.get('password')
        new_user = User(nombre=nombre, apellidos=apellidos, pais=pais, gmail=gmail,password=password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('index')) 
    return render_template('singup.html')

@app.route('/singin', methods=['GET', 'POST'])
def singin():
    if request.method == "POST":
        gmail = request.form.get('gmail')
        password=request.form.get('password')
        user = User.query.filter_by(gmail=gmail).first()
        if user:
           #Logica sintaxis del user
            return redirect(url_for('user_profile', user_id=user.id)) 
        else:
            return 'Usuario no encontrado', 404
    return render_template('singin.html') 

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
        })
    else:
        return jsonify({"error": "Usuario no encontrado"}), 404

@app.route('/productos/<int:product_id>')
def productos(product_id):
    producto=Producto.query.get(product_id)
    return render_template("productos.html",producto=producto)

@app.route('/carrito', methods=["GET","POST"])
def carrito():
    return render_template("carrito.html")

@app.route('/addproducto', methods=["GET","POST"])
def addproducto():
    if request.method=="POST":
        nombre=request.form['nombre']
        precio=request.form['precio']
        categoria=request.form['categoria']
        imagenFile=request.files['imagen']

        if imagenFile and allowed_file(imagenFile.filename):
            ext=imagenFile.filename.split('.')[1]
            filename=secure_filename(f"{nombre}.{ext}")
            imagenFile.save(os.path.join(app.config['UPLOAD_FOLDER'],filename))
        
        urlImg=f"{app.config['UPLOAD_FOLDER']}/{filename}"


        newProducto=Producto(nombre=nombre,precio=precio,categoria=categoria,imagen=urlImg)
        db.session.add(newProducto)
        db.session.commit()
        return render_template("index.html")
    
    categorias=Categoria.query.all()
    return render_template("addproducto.html",categorias=categorias)
        
@app.route('/addcategoria', methods=["GET","POST"])
def addcategoria():
    if request.method=="POST":
        nombre=request.form['nombre']
        db.session.add(Categoria(nombre=nombre))
        db.session.commit()
        return render_template("index.html")
    return render_template("addcategoria.html")

@app.route('/checkout')
def checkout():
    pass

if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.run(debug=True)