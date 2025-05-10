#-----Imports-----#
from flask import Flask, jsonify, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
import os

#-----Configuracion app-----#
app = Flask(__name__)
app.secret_key = 'una_clave_secreta_segura'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///electromarkt.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/img/productos'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024 #Tamaño maximo archivos hasta 16MB
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

#-----Base de datos-----#
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False)
    apellidos = db.Column(db.String(50), nullable=False)
    pais = db.Column(db.String(50), nullable=False)
    gmail = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(50), nullable=False)

class Producto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    precio = db.Column(db.Float, nullable=False)
    imagen = db.Column(db.String(200), nullable=False)
    categoria = db.Column(db.Integer, nullable=False)
    stock = db.Column(db.Integer, nullable=True)
    descripcion = db.Column(db.String(300), nullable=True)

class Categoria(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)

class Carrito(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    idUser = db.Column(db.Integer, nullable=False)

class CarProd(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    idCarrito = db.Column(db.Integer, nullable=False)
    idProd = db.Column(db.Integer, nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)

#-----Funciones globales-----#
def allowed_file(filename):
    return '.' in filename and filename.split('.')[1].lower() in ALLOWED_EXTENSIONS

#-----Inicio Endpoints Web-----#
@app.route('/')
def index():
    categorias = Categoria.query.all()
    productos = Producto.query.all()
    user_id = session.get('user_id')
    return render_template("index.html", productos=productos, categorias=categorias, user_id=user_id)

#-----Enpoints de <Usuarios>-----#
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        apellidos = request.form.get('apellidos')
        pais = request.form.get('pais')
        gmail = request.form.get('gmail')
        password = request.form.get('password')
        new_user = User(nombre=nombre, apellidos=apellidos, pais=pais, gmail=gmail, password=password)
        db.session.add(new_user)
        db.session.commit()
        user=User.query.order_by(User.id.desc()).first()
        session['user_id'] = user.id
        newCarrito=Carrito(user.id)                                 #Creo instancia nuevo carrito
        db.session.add(newCarrito)                                  #Agregar la instancia nueva a los cambios
        db.session.commit()                                         #Subo los cambio a base de datos
        carrito=Carrito.query.order_by(Carrito.id.desc()).first()   #Obtener id de ultimo carrito creado
        return redirect(url_for('index'))
    return render_template('signup.html')

@app.route('/signin', methods=['GET', 'POST'])
def signin():
    if request.method == "POST":
        gmail = request.form.get('gmail')
        password = request.form.get('password')
        user = User.query.filter_by(gmail=gmail, password=password).first()

        if user:
            session['user_id'] = user.id
            return redirect(url_for('user', user_id=user.id))
        else:
            return 'Usuario no encontrado o contraseña incorrecta', 404
    return render_template('signin.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('index'))

@app.route('/user/<int:user_id>')
def user(user_id):
    user = User.query.get(user_id)
    return render_template("users.html", user=user)

#-----Enpoints de <Productos>-----#
@app.route('/productos/<int:product_id>')
def productos(product_id):
    producto = Producto.query.get(product_id)
    return render_template("productos.html", producto=producto)

@app.route('/addproducto', methods=["GET", "POST"])
def addproducto():
    if request.method == "POST":
        nombre = request.form['nombre']
        precio = request.form['precio']
        categoria = request.form['categoria']
        stock = request.form['stock']
        descripcion = request.form['descripcion']
        imagenFile = request.files['imagen']

        if imagenFile and allowed_file(imagenFile.filename):
            ext = imagenFile.filename.split('.')[1]
            filename = secure_filename(f"{nombre}.{ext}")
            imagenFile.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        urlImg = f"{app.config['UPLOAD_FOLDER']}/{filename}"
        newProducto = Producto(nombre=nombre, precio=precio, categoria=categoria, imagen=urlImg, stock=stock, descripcion=descripcion)
        db.session.add(newProducto)
        db.session.commit()
        return redirect(url_for("index"))

    categorias = Categoria.query.all()
    return render_template("addproducto.html", categorias=categorias)

@app.route('/deleteproducto', methods=["GET", "POST"])
def deleteproducto():
    productos = Producto.query.all()
    if request.method == "POST":
        producto = Producto.query.get(request.form['producto'])
        os.system(f"rm {producto.imagen}")
        db.session.delete(producto)
        db.session.commit()
        categorias = Categoria.query.all()
        return render_template('index.html', productos=productos, categorias=categorias)
    return render_template('deleteproducto.html', productos=productos)

#-----Enpoints de <Categorias>-----#
@app.route('/categorias/<int:categoria_id>')
def categorias(categoria_id):
    productos=Producto.query.all()
    categoria=Categoria.query.get(categoria_id)
    return render_template("categorias.html",categoria=categoria, productos=productos)

@app.route('/addcategoria', methods=["GET", "POST"])
def addcategoria():
    if request.method == "POST":
        nombre = request.form['nombre']
        db.session.add(Categoria(nombre=nombre))
        db.session.commit()
        productos = Producto.query.all()
        categorias = Categoria.query.all()
        return render_template("index.html", productos=productos, categorias=categorias)
    return render_template("addcategoria.html")

@app.route('/deletecategoria', methods=["GET", "POST"])
def deletecategoria():
    categorias = Categoria.query.all()
    if request.method == "POST":
        categoria = Categoria.query.get(request.form['categoria'])
        db.session.delete(categoria)
        db.session.commit()
        productos = Producto.query.all()
        return render_template('index.html', productos=productos, categorias=categorias)
    return render_template('deletecategoria.html', categorias=categorias)

#-----Enpoints de <Carritos>-----#
@app.route('/carrito', methods=["GET", "POST"])
def carrito():
    return render_template("carrito.html")

@app.route('/checkout')
def checkout(): #No esta completa, solo tiene la parte final de crear otro carrito
    user_id=session.get('user_id')
    newCarrito=Carrito(idUser=user_id)                          #Creo instancia nuevo carrito
    db.session.add(newCarrito)                                  #Agregar la instancia nueva a los cambios
    db.session.commit()                                         #Subo los cambio a base de datos
    carrito=Carrito.query.order_by(Carrito.id.desc()).first()   #Obtener id de ultimo carrito creado

@app.route('/add_to_cart', methods=["POST"])
def add_to_cart():
    user_id = session.get('user_id')
    carrito=Carrito.query.order_by(Carrito.id.desc()).get(user_id)

    if request.method=="POST":
        producto_id=request.form['product_id']
        producto=Producto.query.get(producto_id)
        newCarProd=CarProd(idCarrito=carrito.id,idProd=producto.id,cantidad=1)
        db.session.add(newCarProd)
        db.session.commit()
    
    #Hacerle un return adecuado

    #Idea, a carrito hay que pasarle la id de a que carrito a de ir

#-----Main-----#
if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.run(debug=True)