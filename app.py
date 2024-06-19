from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from werkzeug.security import check_password_hash, generate_password_hash
from functools import wraps
from werkzeug.utils import secure_filename

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Debes iniciar sesión para acceder a esta página', 'danger')
            return redirect(url_for('login_page'))
        return f(*args, **kwargs)
    return decorated_function

# Inicialización de la aplicación
app = Flask(__name__)
csrf = CSRFProtect(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/tiendafebjul24'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'MiCocoXD'  # este es mi coco

db = SQLAlchemy(app)

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.BigInteger, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False, unique=True)
    email_verified_at = db.Column(db.TIMESTAMP, nullable=True)
    password = db.Column(db.String(255), nullable=False)
    idperfil = db.Column(db.BigInteger, nullable=False, default=3)
    remember_token = db.Column(db.String(100), nullable=True)
    created_at = db.Column(db.TIMESTAMP, nullable=True)
    updated_at = db.Column(db.TIMESTAMP, nullable=True)

class Producto(db.Model):
    __tablename__ = 'productos'
    id = db.Column(db.BigInteger, primary_key=True)
    nombre = db.Column(db.String(255), nullable=False)
    precio = db.Column(db.Integer, nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.TIMESTAMP, nullable=True)
    updated_at = db.Column(db.TIMESTAMP, nullable=True)

class Cliente(db.Model):
    __tablename__ = 'clientes'
    id = db.Column(db.BigInteger, primary_key=True)
    nombre = db.Column(db.String(255), nullable=False)
    rfc = db.Column(db.String(255), nullable=False)
    direccion = db.Column(db.String(255), nullable=False)
    telefono = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.TIMESTAMP, nullable=True)
    updated_at = db.Column(db.TIMESTAMP, nullable=True)

class Perfil(db.Model):
    __tablename__ = 'perfiles'
    id = db.Column(db.BigInteger, primary_key=True)
    nombre = db.Column(db.String(255), nullable=False)

class Factura(db.Model):
    __tablename__ = 'facturas'
    id = db.Column(db.BigInteger, primary_key=True)
    numero = db.Column(db.Integer, nullable=False)
    detalles = db.Column(db.Text, nullable=False)
    valor = db.Column(db.Integer, nullable=False)
    archivo = db.Column(db.String(255), nullable=False)
    idcliente = db.Column(db.BigInteger, db.ForeignKey('clientes.id'), nullable=False)
    idforma = db.Column(db.BigInteger, nullable=False)
    idestado = db.Column(db.BigInteger, nullable=False)
    created_at = db.Column(db.TIMESTAMP, nullable=True)
    updated_at = db.Column(db.TIMESTAMP, nullable=True)

class FormaPago(db.Model):
    __tablename__ = 'formaspago'
    id = db.Column(db.BigInteger, primary_key=True)
    nombre = db.Column(db.String(255), nullable=False)

class EstadoFactura(db.Model):
    __tablename__ = 'estadosfacturas'
    id = db.Column(db.BigInteger, primary_key=True)
    nombre = db.Column(db.String(255), nullable=False)

# Rutas
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login_page():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        user = User.query.filter_by(email=email).first()
        
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['user_name'] = user.name
            flash('Inicio de sesión exitoso', 'success')
            return redirect(url_for('home'))
        else:
            flash('Credenciales incorrectas', 'danger')
    
    return render_template('auth/login.html')

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session.pop('user_id', None)
    session.pop('user_name', None)
    return redirect(url_for('login_page'))

@app.route('/register', methods=['GET', 'POST'])
def register_page():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')  # Método de hash actualizado
        
        new_user = User(name=name, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        
        flash('Usuario registrado exitosamente', 'success')
        return redirect(url_for('login_page'))
    
    return render_template('auth/register.html')

@app.route('/clientes_index')
@login_required
def clientes_index():
    page = request.args.get('page', 1, type=int)
    per_page = 3  # Número de clientes por página

    # Obtener el parámetro de búsqueda por nombre desde la URL
    search = request.args.get('search', '')

    if search:
        # Filtrar los clientes por nombre que contenga la cadena de búsqueda
        clientes_pagination = Cliente.query.filter(Cliente.nombre.ilike(f'%{search}%')).paginate(
            page=page, per_page=per_page, error_out=False)
    else:
        # Si no hay búsqueda, mostrar todos los clientes paginados
        clientes_pagination = Cliente.query.paginate(
            page=page, per_page=per_page, error_out=False)

    return render_template('clientes/index.html', pagination=clientes_pagination, search=search)

@app.route('/clientes_create', methods=['POST'])
@login_required
def clientes_create():
    if request.method == 'POST':

        nombre = request.form['nombre']
        rfc = request.form['rfc']
        direccion = request.form['direccion']
        telefono = request.form['telefono']
        email = request.form['email']
        
        nuevo_cliente = Cliente(nombre=nombre, rfc=rfc, direccion=direccion, telefono=telefono, email=email)
        db.session.add(nuevo_cliente)
        db.session.commit()
        
        flash('Cliente creado exitosamente', 'success')
        return redirect(url_for('clientes_index'))
    else:
        return render_template('clientes/create.html')


@app.route('/clientes_update/<int:id>', methods=['POST'])
@login_required
def clientes_update(id):
    cliente = Cliente.query.get_or_404(id)
    if request.method == 'POST':
        cliente.nombre = request.form['nombre']
        cliente.rfc = request.form['rfc']
        cliente.direccion = request.form['direccion']
        cliente.telefono = request.form['telefono']
        cliente.email = request.form['email']
        
        db.session.commit()
        
        flash('Cliente actualizado exitosamente', 'success')
        return redirect(url_for('clientes_index'))

@app.route('/clientes_destroy/<int:id>', methods=['POST'])
@login_required
def clientes_destroy(id):
    cliente = Cliente.query.get_or_404(id)
    db.session.delete(cliente)
    db.session.commit()
    flash('Cliente eliminado exitosamente', 'success')
    return redirect(url_for('clientes_index'))

@app.route('/perfiles_index')
@login_required
def perfiles_index():
    page = request.args.get('page', 1, type=int)
    per_page = 3  # Número de perfiles por página
    search = request.args.get('search', '')

    if search:
        perfiles = Perfil.query.filter(Perfil.nombre.ilike(f'%{search}%')).paginate(page=page, per_page=per_page, error_out=False)
    else:
        perfiles = Perfil.query.paginate(page=page, per_page=per_page, error_out=False)

    return render_template('perfiles/index.html', perfiles=perfiles, search=search)

@app.route('/perfiles_create', methods=['POST'])
@login_required
def perfiles_create():
    if request.method == 'POST':
        nombre = request.form['nombre']
        
        nuevo_perfil = Perfil(nombre=nombre)
        db.session.add(nuevo_perfil)
        db.session.commit()
        
        flash('Perfil creado exitosamente', 'success')
        return redirect(url_for('perfiles_index'))
    else:
        return render_template('perfiles/create.html')

@app.route('/perfiles_update/<int:id>', methods=['POST'])
@login_required
def perfiles_update(id):
    perfil = Perfil.query.get_or_404(id)
    if request.method == 'POST':
        perfil.nombre = request.form['nombre']
        
        db.session.commit()
        
        flash('Perfil actualizado exitosamente', 'success')
        return redirect(url_for('perfiles_index'))

@app.route('/perfiles_destroy/<int:id>', methods=['POST'])
@login_required
def perfiles_destroy(id):
    perfil = Perfil.query.get_or_404(id)
    db.session.delete(perfil)
    db.session.commit()
    flash('Perfil eliminado exitosamente', 'success')
    return redirect(url_for('perfiles_index'))

@app.route('/facturas_index')
@login_required
def facturas_index():
    page = request.args.get('page', 1, type=int)
    per_page = 3  # Número de facturas por página
    facturas_pagination = Factura.query.paginate(page=page, per_page=per_page, error_out=False)
    clientes = Cliente.query.all()
    formaspago = FormaPago.query.all()
    estadosfacturas = EstadoFactura.query.all()
    return render_template('facturas/index.html', 
                           facturas=facturas_pagination.items, 
                           pagination=facturas_pagination, 
                           clientes=clientes, 
                           formaspago=formaspago, 
                           estadosfacturas=estadosfacturas)

@app.route('/facturas_store', methods=['POST'])
@login_required
def facturas_store():
    if request.method == 'POST':
        numero = request.form['numero']
        detalles = request.form['detalles']
        valor = request.form['valor']
        archivo = request.files['archivo']
        idcliente = request.form['idcliente']
        idforma = request.form['idforma']
        idestado = request.form['idestado']

        # Obtener el nombre del archivo
        filename = archivo.filename

        # Guardar la factura en la base de datos con el nombre del archivo
        nueva_factura = Factura(numero=numero, detalles=detalles, valor=valor, archivo=filename, idcliente=idcliente, idforma=idforma, idestado=idestado)
        db.session.add(nueva_factura)
        db.session.commit()

        flash('Factura creada exitosamente', 'success')
        return redirect(url_for('facturas_index'))

@app.route('/facturas_update/<int:id>', methods=['POST'])
@login_required
def facturas_update(id):
    if request.method == 'POST':
        factura = Factura.query.get_or_404(id)
        numero = request.form['numero']
        detalles = request.form['detalles']
        valor = request.form['valor']
        idcliente = request.form['idcliente']
        idforma = request.form['idforma']
        idestado = request.form['idestado']

        # Obtener el nombre del archivo
        archivo = request.files['archivo']
        filename = archivo.filename

        # Actualizar los campos de la factura
        factura.numero = numero
        factura.detalles = detalles
        factura.valor = valor
        factura.idcliente = idcliente
        factura.idforma = idforma
        factura.idestado = idestado

        # Si se cargó un archivo, actualizar el nombre del archivo
        if filename:
            factura.archivo = filename

        # Guardar los cambios en la base de datos
        db.session.commit()

        flash('Factura actualizada exitosamente', 'success')
        return redirect(url_for('facturas_index'))

@app.route('/facturas_destroy/<int:id>', methods=['POST'])
@login_required
def facturas_destroy(id):
    factura = Factura.query.get_or_404(id)
    db.session.delete(factura)
    db.session.commit()
    flash('Factura eliminada exitosamente', 'success')
    return redirect(url_for('facturas_index'))

@app.route('/productos_index')
@login_required
def productos_index():
    productos = Producto.query.all()  # Suponiendo que tienes un modelo llamado Producto que mapea la tabla 'productos'
    return render_template('productos/index.html', productos=productos)

@app.route('/carrito_index')
@login_required
def carrito_index():
    return render_template('carrito.html')

# Ejecución de la aplicación
if __name__ == '__main__':
    app.run(debug=True)