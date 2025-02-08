from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, send_from_directory
from .models import Product, Cart, Order
from . import db, mail
from flask_login import login_required, current_user
from intasend import APIService
from .forms import ContactForm
from flask_mail import Message
import stripe

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
    
    if item_to_add.in_stock:
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
        flash(f'item out of stock', 'danger')
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
        print(cart_item)
        cart = Cart.query.filter_by(customer_id=current_user.id).all()
        if cart_item.quantity < cart_item.product.in_stock:
            cart_item.quantity = cart_item.quantity + 1
        db.session.commit()
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
        if cart_item.quantity > 1:
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
    
    

@views.route('/About_us')
def about():
    '''About us route'''
    return render_template('about_us.html')


@views.route('/place_order', methods=['POST'])
@login_required
def place_order():
    """
    Place an order for the items in the customer's cart.
    Processes the order based on the selected payment method.
    """
    payment_method = request.form.get('payment_method')
    print(payment_method)
    
    if not payment_method:
        flash('Please select a payment method', 'danger')
        return redirect(request.referrer)
    
    customer_cart = Cart.query.filter_by(customer_id=current_user.id).all()
    if not customer_cart:
        flash('Your cart is empty!', 'danger')
        return redirect('/')
    
    if payment_method == 'cod':
        # Process order for Cash on Delivery
        try:
            total = 0
            for item in customer_cart:
                total += item.product.current_price * item.quantity

            # Process each cart item and create orders
            for item in customer_cart:
                new_order = Order()
                new_order.quantity = item.quantity
                new_order.price = item.product.current_price
                new_order.product_id = item.product_id
                new_order.customer_id = current_user.id
                # Optionally, save the payment method for future reference
                new_order.payment_method = 'Cash on Delivery'
                db.session.add(new_order)
                
                # Update product inventory
                product = Product.query.get(item.product_id)
                product.in_stock -= item.quantity
                # Remove the item from the cart
                db.session.delete(item)
            
            # Commit after processing all items
            db.session.commit()
            flash('Order placed successfully with Cash on Delivery!', 'success')
            return redirect('/orders')
        except Exception as e:
            print(e)
            db.session.rollback()
            flash('An error occurred while placing the order', 'danger')
            return redirect(request.referrer)
    
    elif payment_method == 'credit_card':
        # Redirect to your credit card payment processing (e.g., Stripe Checkout)
        # You should implement your Stripe integration in a separate route.
        return redirect(url_for('views.stripe_checkout'))
    else:
        flash('Invalid payment method selected', 'danger')
        return redirect(request.referrer)




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
    items = Product.query.filter_by(category='Smartphones').all()
    print(items)
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
    
    
    
    
@views.route('/contact', methods=['GET', 'POST'])
def contact():
    """
    Renders the contact_us.html template and handles the contact form submission.

    Returns:
        If the form is submitted successfully, it redirects to the 'contact' view.
        Otherwise, it renders the 'contact_us.html' template with the contact form.
    """
    form = ContactForm()
    if form.validate_on_submit():
        msg = Message(form.subject.data,
                      sender=form.email.data,
                      recipients=['sanadmhmoud76@gmail.co'])
        msg.body = f'''Name: {form.name.data}
Email: {form.email.data}
Message: {form.message.data}
'''
        mail.send(msg)
        flash('Your message has been sent successfully!', 'success')
        return redirect(url_for('views.contact'))
    return render_template('contact_us.html', form=form)




# Handle the Stripe checkout 

@views.route('/stripe_checkout', methods=['GET'])
@login_required
def stripe_checkout():
    # Retrieve the customer's cart items
    customer_cart = Cart.query.filter_by(customer_id=current_user.id).all()
    if not customer_cart:
        flash('Your cart is empty!', 'danger')
        return redirect('/')
    
    # Build the line items for Stripe Checkout.
    # Stripe expects the amount in cents, so multiply by 100 (and ensure the price is an integer or convert it).
    line_items = []
    for item in customer_cart:
        line_item = {
            'price_data': {
                'currency': 'EGP',  # Change this to your desired currency
                'unit_amount': int(item.product.current_price),  # Stripe requires the amount in cents
                'product_data': {
                    'name': item.product.product_name,
                    # Optionally add more product details (like description)
                },
            },
            'quantity': item.quantity,
        }
        line_items.append(line_item)
    
    try:
        # Create a Stripe Checkout Session
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=line_items,
            mode='payment',
            # Replace 'payment_success' and 'payment_cancel' with your actual route names.
            success_url=url_for('views.payment_success', _external=True) + '?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=url_for('views.payment_cancel', _external=True),
        )
        # Redirect to the Stripe Checkout page
        return redirect(session.url, code=303)
    except Exception as e:
        print(e)
        flash('An error occurred while initiating the payment process', 'danger')
        return redirect(url_for('views.cart'))
    
    
    
    
@views.route('/payment_success')
@login_required
def payment_success():
    # Here you could verify the session and update order status if needed.
    flash('Payment successful! Your order is being processed.', 'success')
    return redirect('/orders')



@views.route('/payment_cancel')
@login_required
def payment_cancel():
    flash('Payment canceled. Please try again.', 'danger')
    return redirect(url_for('views.cart'))

