from flask import Flask , render_template
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager 
from flask_mail import Mail
import os



db = SQLAlchemy()
bcrypt = Bcrypt()
mail = Mail()

def create_database():
    db.create_all()
    print('Created Database!')
 

app = Flask(__name__, template_folder='templates', static_folder='static')
app.config['SECRET_KEY'] = os.urandom(24)
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql+psycopg2://kenany_user:Im0bVJnHWP7rB2Ac5Iimr9FYffmPg8yF@dpg-cpmfn7g8fa8c73ahtvsg-a/kenany_store_v2"

# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://kenany_user:yourpassword@localhost/kenany_store'

# Initialize the database
db.init_app(app)





@app.errorhandler(404)
def page_not_found(erorr):
    return render_template('404.html'), 404

# Flask-Login Configuration
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'

@login_manager.user_loader
def load_user(id):
    return Customer.query.get(int(id))

# Initialize the mail
app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'faresosama002@gmail.com'
app.config['MAIL_PASSWORD'] = 'oasw ahyv yqoz bvjt'
mail = Mail(app)

# Register Blueprints
from .views import views
from .admin import admin
from .auth import auth
from .models import Customer, Product, Order,  Cart

app.register_blueprint(views, url_prefix='/')
app.register_blueprint(admin, url_prefix='/')
app.register_blueprint(auth, url_prefix='/')

with app.app_context():
    create_database()
