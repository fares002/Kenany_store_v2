from flask import Blueprint, render_template, redirect, url_for, flash, send_from_directory
from flask_login import login_required, current_user
from .forms import ShopItemsForm, OrdersForm, CategoryForm
from werkzeug.utils import secure_filename
from .models import Product , Order , Customer
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from . import db


admin = Blueprint('admin', __name__)



@admin.route('/media/<filename>')
def get_media(filename):
    """Route for serving media files."""
    return send_from_directory('../media', filename)


@admin.route('/add_shop_items', methods=['GET', 'POST'])
@login_required
def add_shop_items():
    """
    Add new shop items to the database.

    This function allows an admin user to add new shop items to the database. It validates the form data,
    saves the uploaded product picture, creates a new `Product` object, and adds it to the database.

    Returns:
        If the product is added successfully, it redirects to the `add_shop_items` page.
        If there is a duplicate entry for the product name, it displays an error message and does not add the product.
        If there is an error while adding the product, it displays an error message and does not add the product.
        If the current user is not an admin, it renders the `404.html` template.

    """
    if current_user.id == 1:
        form = ShopItemsForm()
        Category = CategoryForm()
        
        if form.validate_on_submit():
            # Get form data
            product_name = form.product_name.data
            current_price = form.current_price.data
            previous_price = form.previous_price.data if form.previous_price.data else None,
            in_stock = form.in_stock.data
            flash_sale = form.flash_sale.data
            featured_product = form.featured_product.data
            description = form.description.data
            category = Category.category.data
            file = form.product_picture.data
            
            # Save the uploaded product picture
            file_name = secure_filename(file.filename)
            file_path = f'./media/{file_name}'
            file.save(file_path)

            # Create a new Product object
            new_shop_item = Product()
            new_shop_item.product_name = product_name
            new_shop_item.current_price = current_price
            new_shop_item.previous_price = previous_price
            new_shop_item.in_stock = in_stock
            new_shop_item.flash_sale = flash_sale
            new_shop_item.featured_product = featured_product
            new_shop_item.description = description
            new_shop_item.category = category
            new_shop_item.image = file_path

            try:
                db.session.add(new_shop_item)
                db.session.commit()
                flash(f'{product_name} added Successfully', 'success')
                print('Product Added Successfully!!')
                return redirect(url_for('admin.add_shop_items'))
            except IntegrityError:
                db.session.rollback()
                flash(f'Product with name {product_name} already exists.', 'danger')
                print('Duplicate entry for product name.')
            except SQLAlchemyError as e:
                db.session.rollback()
                flash('An error occurred while adding the product.', 'danger')
                print(f'SQLAlchemy Error: {e}')
                
        print(form.errors)
        return render_template('add_shop_items.html', form=form, Category=Category)
    return render_template('404.html')




@admin.route('/shop_items', methods=['GET', 'POST'])
@login_required
def shop_items():
    """
    Render the shop items page.

    If the current user's ID is 1, retrieve all products from the database
    and render the 'shop_items.html' template with the retrieved items.
    Otherwise, render the '404.html' template.

    Returns:
        The rendered template.
    """
    if current_user.id == 1:
        items = Product.query.order_by(Product.created_at).all()
        return render_template('shop_items.html', items=items)

    return render_template('404.html')



@admin.route('update_item/<int:id>', methods=['GET', 'POST'])
@login_required
def update_shop_item(id):
    """
    Update a shop item with the given ID.

    Parameters:
    - id (int): The ID of the shop item to update.

    Returns:
    - flask.Response: The response object to render the update_item.html template or redirect to admin.shop_items.

    Raises:
    - None.

    """
    if current_user.id == 1:
        form= ShopItemsForm()
        Category = CategoryForm()
        item_to_update = Product.query.get(id)
        form.product_name.render_kw = {'value': item_to_update.product_name}
        form.current_price.render_kw = {'value': item_to_update.current_price}
        form.previous_price.render_kw = {'value': item_to_update.previous_price}
        form.in_stock.render_kw = {'value': item_to_update.in_stock}
        form.description.render_kw = {'value': item_to_update.description}
        Category.category.render_kw = {'value': item_to_update.category}
        form.flash_sale.render_kw = {'checked': item_to_update.flash_sale}
        form.featured_product.render_kw = {'checked': item_to_update.featured_product}
        
        if form.validate_on_submit():
            product_name = form.product_name.data
            current_price = form.current_price.data
            previous_price = form.previous_price.data
            in_stock = form.in_stock.data
            description = form.description.data
            category = Category.category.data
            flash_sale = form.flash_sale.data
            featured_product = form.featured_product.data
            
            file = form.product_picture.data
            file_name = secure_filename(file.filename)
            file_path = f'./media/{file_name}'
            file.save(file_path)
            
            try:
                Product.query.filter_by(id=id).update(dict(
                                                            product_name=product_name,
                                                            current_price=current_price,
                                                            previous_price=previous_price,
                                                            in_stock=in_stock,
                                                            description=description,
                                                            category=category,
                                                            flash_sale=flash_sale,
                                                            featured_product=featured_product,
                                                            image=file_path
                                                        ))
                
                db.session.commit()
                flash('Item Updated Successfully', 'success')
                return redirect(url_for('admin.shop_items'))
            except IntegrityError:
                db.session.rollback()
                flash(f'Product with name {product_name} already exists.', 'danger')
                print('Duplicate entry for product name.')
            except SQLAlchemyError as e:
                db.session.rollback()
                flash('An error occurred while adding the product.', 'danger')
                print(f'SQLAlchemy Error: {e}')
                
         
        return render_template('update_item.html', form=form, Category=Category)
    
    return render_template('404.html')



@admin.route('/delete_item/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_item(id):
    """
    Delete an item from the database.

    Args:
        id (int): The ID of the item to be deleted.

    Returns:
        flask.Response: A redirect response to the 'admin.shop_items' route.

    Raises:
        Exception: If an error occurs during the deletion process.

    """
    if current_user.id == 1:
        try:
            item_to_delete = Product.query.get(id)
            db.session.delete(item_to_delete)
            db.session.commit()
            flash('Item Deleted Successfully', 'success')
            return redirect(url_for('admin.shop_items'))
        except Exception as e:
            print(e)
            flash("Item Not Deleted!!", 'danger')
        return redirect(url_for('admin.shop_items'))
        
    return render_template('404.html')



@admin.route('/view_orders', methods=['GET', 'POST'])
@login_required
def view_orders():
    """
    View orders function.

    This function is responsible for rendering the orders page. If the current user's ID is 1,
    it retrieves all orders from the database and renders the 'view_orders.html' template with
    the orders data. Otherwise, it renders the '404.html' template.

    Returns:
        The rendered template for the orders page or the '404.html' template.

    """
    if current_user.id == 1:
        orders = Order.query.order_by(Order.created_at).all()
        return render_template('view_orders.html', orders=orders)
    
    return render_template('404.html')




@admin.route('/update_order/<int:id>', methods=['GET', 'POST'])
@login_required
def update_order(id):
    """
    Update the status of an order with the given ID.

    Args:
        id (int): The ID of the order to update.

    Returns:
        flask.Response: A response object that redirects to the appropriate page.

    Raises:
        Exception: If there is an error updating the order status.

    """
    if current_user.id == 1:
        form = OrdersForm()
        
        if form.validate_on_submit():
            order = Order.query.get(id)
            order_status = form.order_status.data
            try:
                order.status = order_status
                db.session.commit()
                flash('Order Status Updated Successfully', 'success')
                return redirect(url_for('admin.view_orders'))
            except Exception as e:
                print(e)
                flash('Order Status Not Updated!!', 'danger')
                return redirect(url_for('admin.update_order', id=id))
        
        return render_template('update_order.html', form=form)
    return render_template('404.html')




@admin.route('/customers', methods=['GET', 'POST'])
@login_required
def customers():
    """
    Retrieve and render a list of customers.

    If the current user's ID is 1, the function retrieves all customers from the database
    and renders them in the 'customers.html' template. Otherwise, it renders the '404.html'
    template.

    Returns:
        The rendered template with the list of customers or the '404.html' template.

    """
    if current_user.id == 1:
        customers = Customer.query.order_by(Customer.created_at).all()
        return render_template('customers.html', customers=customers)
    
    return render_template('404.html')

