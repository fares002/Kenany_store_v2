from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, send_from_directory
from .models import Product, Cart, Order
from . import db
from flask_login import login_required, current_user
from intasend import APIService

views = Blueprint('views', __name__)
API_PUBLISHABLE_KEY = "ISPubKey_test_8ff503c9-81b7-4144-88df-4ce1d65a3cdb"
API_TOKEN = "ISSecretKey_test_2d424435-3893-4eb4-ae0f-e0a7e8736288"


@views.route('/media/<filename>')
def get_media(filename):
    """
    Route to get media files from the media folder
    """
    return send_from_directory('../media', filename)


@views.route('/home')
def home():
    """
    Renders the home page of the website.
    
    Retrieves all products from the database and passes them to the home.html template.
    If the user is authenticated, it also retrieves the cart items for the current user.
    
    Returns:
        The rendered home.html template with the products and cart items.
    """
    items = Product.query.all()
    return render_template('home.html', items=items, cart=Cart.query.filter_by(customer_id=current_user.id).all()
                           if current_user.is_authenticated else [])


@views.route('/')
def base():
    """
    This function retrieves flash sale items and featured products from the database and renders the landing page template.
    
    Returns:
        A rendered template with flash sale items, featured products, and the customer's cart (if authenticated).
    """
    items = Product.query.filter_by(flash_sale=True).all()
    featured_items = Product.query.filter_by(featured_product=True).all()
    return render_template('landing_page.html', items=items, featured_items=featured_items,
                           cart=Cart.query.filter_by(customer_id=current_user.id).all()
                           if current_user.is_authenticated else [])


@views.route('/add_to_cart/<int:id>', methods=['POST', 'GET'])
@login_required
def add_to_cart(id):
    """
    Add an item to the cart.

    Args:
        id (int): The ID of the product to add to the cart.

    Returns:
        flask.Response: A redirect response to the previous page.

    Raises:
        Exception: If an error occurs while adding the item to the cart.

    """
    item_to_add = Product.query.get(id) #get item to add to cart
    item_exists = Cart.query.filter_by(product_id=id, customer_id=current_user.id).first() #check if item already exists in cart for user
    if item_exists:
        try:
            item_exists.quantity += 1
            db.session.commit()
            flash('item added to cart successfully!', 'success')
            return redirect(request.referrer)
        except Exception as e:
            print(e)
            flash(f'An error occurred while adding item to cart', 'danger')
            return redirect(request.referrer)
    
    new_cart_item = Cart()
    new_cart_item.quantity = 1
    new_cart_item.product_id = item_to_add.id
    new_cart_item.customer_id = current_user.id
    
    try:
        db.session.add(new_cart_item)
        db.session.commit()
        flash(f'added to cart successfully!', 'success')
        return redirect(request.referrer)
    except Exception as e:
        print(e)
        flash(f'An error occurred while adding item to cart', 'danger')
        return redirect(request.referrer)


@views.route('/cart', methods=['POST', 'GET'])
@login_required
def cart():
    '''
    Render the cart page with the cart items, amount, and total.

    Returns:
        rendered template: The rendered HTML template for the cart page.
    '''
    cart_items = []
    amount = 0
    total = 0
    if current_user.is_authenticated:
        id = current_user.id
        cart_items = Cart.query.filter_by(customer_id=id).all()
        for item in cart_items:
            amount = amount + item.product.current_price * item.quantity
            total = amount + 1000
        print(current_user.id, cart_items, amount, total)
    return render_template('cart.html', cart_items=cart_items , amount=amount, total=total)


@views.route('/delete_cart_item/<int:id>', methods=['POST', 'GET'])
@login_required
def delete_cart_item(id):
    """
    Delete a cart item from the database.

    Args:
        id (int): The ID of the cart item to be deleted.

    Returns:
        redirect: A redirect response to the previous page.

    Raises:
        Exception: If an error occurs while deleting the item.

    """
    item_to_delete = Cart.query.get(id)
    try:
        db.session.delete(item_to_delete)
        db.session.commit()
        # flash('item deleted successfully!', 'success')
        return redirect(request.referrer)
    except Exception as e:
        print(e)
        flash('An error occurred while deleting item', 'danger')
        return redirect(request.referrer)

    
@views.route('/pluscart')
def pluscart():
    if request.method == 'GET':
        prod_id = request.args.get('prod_id')
        cart_item = Cart.query.get(prod_id)
       
        cart_item.quantity = cart_item.quantity + 1
        db.session.commit()
        cart = Cart.query.filter_by(customer_id=current_user.id).all()
        amount = 0
        for item in cart:
            amount = amount + item.product.current_price * item.quantity
            total = amount + 1000
            print(amount, total, cart_item.quantity)
        data = {
            'quantity': cart_item.quantity,
            'amount': amount,
            'total': total
        }
        return jsonify(data)

       
@views.route('/minuscart')
def minuscart():
    """
    Decreases the quantity of a product in the cart by 1.

    Returns:
        A JSON response containing the updated quantity, amount, and total.
    """
    if request.method == 'GET':
        prod_id = request.args.get('prod_id')
        cart_item = Cart.query.get(prod_id)
        if cart_item.quantity:
            cart_item.quantity = cart_item.quantity - 1
            db.session.commit()
            cart = Cart.query.filter_by(customer_id=current_user.id).all()
            amount = 0
            for item in cart:
                amount = amount + item.product.current_price * item.quantity
                total = amount + 1000
                print(amount, total, cart_item.quantity)
            data = {
                'quantity': cart_item.quantity,
                'amount': amount,
                'total': total
            }
        return jsonify(data)
    
    
# @views.route('/remove_cart_item', methods=['POST', 'GET'])
# @login_required
# def remove_cart_item():
#     if request.method == 'GET':
#         prod_id = request.args.get('prod_id')
        
#         # Check if prod_id is provided
#         if not prod_id:
#             return jsonify({'error': 'Product ID not provided'}), 400
        
#         # Check if prod_id is valid and corresponding cart_item exists
#         cart_item = Cart.query.get(prod_id)
#         if not cart_item:
#             return jsonify({'error': 'Cart item not found'}), 404
        
#         # Ensure the cart item belongs to the current user
#         if cart_item.customer_id != current_user.id:
#             return jsonify({'error': 'Unauthorized action'}), 403

#         db.session.delete(cart_item)
#         db.session.commit()
#         cart = Cart.query.filter_by(customer_id=current_user.id).all()
#         amount = sum(item.product.current_price * item.quantity for item in cart)
#         total = amount + 1000

#         data = {
#             'quantity': 3,
#             'amount': amount,
#             'total': total
#         }
#         return jsonify(data)




@views.route('/About_us')
def about():
    '''About us route'''
    return render_template('about_us.html')


@views.route('/place_order', methods=['POST', 'GET'])
@login_required
def place_order():
    """
    Place an order for the items in the customer's cart.
    
    This function calculates the total amount for the items in the customer's cart,
    creates an order using an external API service, updates the inventory, and
    redirects the user to the orders page if the order is placed successfully.
    
    Returns:
        A redirect response to the orders page if the order is placed successfully,
        or a redirect response to the previous page with an error message if an error occurs.
    """
    customer_cart = Cart.query.filter_by(customer_id=current_user.id).all()
    if customer_cart:
        try:
            total = 0
            for item in customer_cart:
                total += item.product.current_price * item.quantity
            service = APIService(token=API_TOKEN, publishable_key=API_PUBLISHABLE_KEY, test=True)
            create_order_response = service.collect.mpesa_stk_push(phone_number="2541557636517", email=current_user.email, amount=total, currency="USD", narrative="Purchase of goods")
            
            for item in customer_cart:
                new_order = Order()
                new_order.quantity = item.quantity
                new_order.price = item.product.current_price
                new_order.status = create_order_response['invoice']['state'].capitalize()
                new_order.payment_id = create_order_response['id']
                
                new_order.product_id = item.product_id
                new_order.customer_id = current_user.id
                db.session.add(new_order)
                
                product = Product.query.get(item.product_id)
                product.in_stock -= item.quantity
                db.session.delete(item)
                db.session.commit()
                
            flash('Order placed successfully!', 'success')
            return redirect('/orders')
        except Exception as e:
            print(e)
            flash('An error occurred while placing order', 'danger')
            return redirect(request.referrer)
    
    flash('Your cart is empty!', 'danger')
    return redirect('/')



@views.route('/orders' , methods=['POST', 'GET'])
@login_required
def orders():
    """
    Retrieve and display the orders for the current user.

    Returns:
        A rendered template 'orders.html' with the orders data.
    """
    orders = Order.query.filter_by(customer_id=current_user.id).all()
    for item in orders:
        print(item.product.product_name)
    return render_template('orders.html', orders=orders)
    
    

@views.route('/search', methods=['POST', 'GET'])
def search():
    """
    Perform a search based on the provided search term.

    If the request method is POST, the function retrieves the search term from the form data.
    It then queries the database for products whose names contain the search term (case-insensitive).
    The function also retrieves the cart items for the current user (if authenticated) and renders the search results.

    If no search term is provided, the function renders an empty search result with an error message.

    If the request method is not POST, the function redirects to the home page.

    Returns:
        A rendered template with the search results or a redirect to the home page.
    """
    if request.method == 'POST':
        search = request.form.get('search')
        if search:
            items_new = Product.query.filter(Product.product_name.ilike(f'%{search}%')).all()
            cart_items = Cart.query.filter_by(customer_id=current_user.id).all() if current_user.is_authenticated else []
            return render_template('search.html', items_new=items_new, cart=cart_items)
        else:
            # Return an error message or an empty search result if no search term is provided
            return render_template('search.html', items_new=[], cart=cart_items, error="No search term provided.")
    else:
        # Handle GET requests or return a default response
        return redirect(url_for('views.home'))



@views.route('/products/<int:product_id>')
def product_detail(product_id):
    """
    Display the details of a product.

    Args:
        product_id (int): The ID of the product to display.

    Returns:
        A rendered template displaying the product details.

    """
    product_detail = Product.query.filter_by(id=product_id).first() 
    print(product_detail.image)
    return render_template('product_detail.html', product=product_detail, cart=Cart.query.filter_by(customer_id=current_user.id).all()
                           if current_user.is_authenticated else [])
    

@views.route('/category/Smartphones')
def smartphones():
    """
    Renders the smartphones.html template with a list of smartphones and the user's cart.

    Returns:
        The rendered template with the list of smartphones and the user's cart.
    """
    items = Product.query.filter_by(category='smartphones').all()
    return render_template('smartphones.html', items=items, cart=Cart.query.filter_by(customer_id=current_user.id).all()
                           if current_user.is_authenticated else [])
    
    
    
@views.route('/category/Headphones and Speakers')
def Headphones_and_Speakers():
    """
    Renders the 'Headphones and Speakers' page with the list of items in the 'Headphones and Speakers' category.
    
    Returns:
        A rendered template of the 'Headphones and Speakers' page with the items and the user's cart.
    """
    items = Product.query.filter_by(category='Headphones and Speakers').all()
    return render_template('Headphones and Speakers.html', items=items, cart=Cart.query.filter_by(customer_id=current_user.id).all()
                           if current_user.is_authenticated else [])
    
    
    
@views.route('/category/Laptops')
def Laptops():
    """
    Retrieve all laptops from the database and render the 'Laptops.html' template.

    Returns:
        The rendered template with the retrieved laptops and the user's cart (if authenticated).
    """
    items = Product.query.filter_by(category='Laptops').all()
    return render_template('Laptops.html', items=items, cart=Cart.query.filter_by(customer_id=current_user.id).all()
                           if current_user.is_authenticated else [])
    
    
   
@views.route('/category/Accessories')
def Accessories():
    """
    Render the Accessories page with the list of accessories items.

    Returns:
        rendered template: The rendered template for the Accessories page.
    """
    items = Product.query.filter_by(category='Accessories').all()
    return render_template('Accessories.html', items=items, cart=Cart.query.filter_by(customer_id=current_user.id).all()
                           if current_user.is_authenticated else [])
