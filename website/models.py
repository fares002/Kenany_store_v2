from . import db, bcrypt, app
from datetime import datetime, timedelta
from flask_login import UserMixin
import jwt




class Base(db.Model):
    """
    Base class for all models in the application.

    Attributes:
        id (int): The primary key of the model.
        created_at (datetime): The timestamp when the model was created.
        updated_at (datetime): The timestamp when the model was last updated.

    Methods:
        __str__(): Returns a string representation of the BaseModel class.
    """

    __abstract__ = True
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __str__(self):
        """String representation of the BaseModel class"""
        return "[{:s}] ({:s}) {}".format(self.__class__.__name__, str(self.id), self.__dict__)

class Customer(Base, UserMixin):
    """
    Represents a customer in the system.

    Attributes:
        username (str): The username of the customer.
        email (str): The email address of the customer.
        password_hash (str): The hashed password of the customer.
        first_name (str): The first name of the customer.
        last_name (str): The last name of the customer.
        phone_number (str): The phone number of the customer.
        address (str): The address of the customer.
        profile_pic (str): The filename of the customer's profile picture.
        date_joined (datetime): The date and time when the customer joined.
        cart_items (list): The list of cart items associated with the customer.
        orders (list): The list of orders placed by the customer.
        reviews (list): The list of reviews written by the customer.
        wishlist_items (list): The list of wishlist items of the customer.
    """

    __tablename__ = 'customers'
    username = db.Column(db.String(150), unique=True, index=True, nullable=False)
    email = db.Column(db.String(150), unique=True, index=True, nullable=False)
    password_hash = db.Column(db.String(150), nullable=False)
    first_name = db.Column(db.String(150), nullable=True)
    last_name = db.Column(db.String(150), nullable=True)
    phone_number = db.Column(db.String(15), nullable=False) 
    address = db.Column(db.String(150), nullable=False)
    profile_pic = db.Column(db.String(150), default='default.jpg', nullable=True)
    date_joined = db.Column(db.DateTime, default=datetime.utcnow)
    cart_items = db.relationship('Cart', backref='customer', lazy=True)
    orders = db.relationship('Order', backref='customer', lazy=True)
    reviews = db.relationship('Review', back_populates='customer', lazy=True)
    wishlist_items = db.relationship('Wishlist', backref='customer', lazy=True)
    
    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')
    
    @password.setter
    def password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
    
    def verify_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<Customer {self.username}>'
    
    
    def get_reset_token(self, expire_time=1800):
        expire = datetime.utcnow() + timedelta(seconds=expire_time)
        token = jwt.encode(
            {'user_id': self.id, 'exp': expire},
            app.config['SECRET_KEY'],
            algorithm='HS256'
        )
        return token

    @staticmethod
    def verify_reset_token(token):
        try:
            decoded = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            user_id = decoded['user_id']
        except jwt.ExpiredSignatureError:
            return None  # Token has expired
        except jwt.InvalidTokenError:
            return None  # Invalid token
        return Customer.query.get(user_id)
    
    


class Product(Base):
    """
    Represents a product in the inventory.

    Attributes:
        product_name (str): The name of the product.
        current_price (float): The current price of the product.
        previous_price (float): The previous price of the product.
        description (str): The description of the product.
        in_stock (int): The quantity of the product in stock.
        image (str): The URL or path to the product image.
        flash_sale (bool): Indicates if the product is on a flash sale.
        featured_product (bool): Indicates if the product is a featured product.
        category (str): The category of the product.
        cart_items (list): A list of cart items associated with the product.
        orders (list): A list of orders associated with the product.
        reviews (list): A list of reviews associated with the product.
    """

    __tablename__ = 'products'
    product_name = db.Column(db.String(150), unique=True, nullable=False, index=True)
    current_price = db.Column(db.Float, nullable=False)
    previous_price = db.Column(db.Float, nullable=True)
    description = db.Column(db.String(1000), nullable=True)
    in_stock = db.Column(db.Integer, default=1)
    image = db.Column(db.String(1000), nullable=True)
    flash_sale = db.Column(db.Boolean, default=False)
    featured_product = db.Column(db.Boolean, default=False)
    category = db.Column(db.String(150), nullable=False)
    cart_items = db.relationship('Cart', backref='product', lazy=True)
    orders = db.relationship('Order', backref='product', lazy=True)
    reviews = db.relationship('Review', back_populates='product', lazy=True)
    
    def __str__(self):
        return f'<Product {self.product_name}>'

class Cart(Base):
    """
    Represents a cart item in the website.
    
    Attributes:
        quantity (int): The quantity of the product in the cart.
        customer_id (int): The ID of the customer who owns the cart.
        product_id (int): The ID of the product in the cart.
    """
    
    __tablename__ = 'carts'
    quantity = db.Column(db.Integer, default=1)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    
    def __str__(self):
        return f'<Cart {self.id}>'

class Order(Base):
    """
    Represents an order in the system.
    """

    __tablename__ = 'orders'
    quantity = db.Column(db.Integer, default=1)
    price = db.Column(db.Float, nullable=False)
    paid = db.Column(db.Boolean, default=False)
    status = db.Column(db.String(150), default='Pending', nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    payment_id = db.Column(db.String(1000))
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    
    def __str__(self):
        return f'<Order {self.id}>'




class Review(Base):
    """
    Represents a review for a product made by a customer.
    """

    __tablename__ = 'reviews'
    rating = db.Column(db.Integer, nullable=False)  # Assuming rating is an integer
    comment = db.Column(db.Text, nullable=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    
    customer = db.relationship('Customer', back_populates='reviews')
    product = db.relationship('Product', back_populates='reviews')

    def __str__(self):
        return f'<Review {self.id} for Product {self.product_id}>'

 
class Wishlist(Base):
    """ Wishlist Model"""
    user_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    product = db.relationship('Product', backref='wishlist_items')

