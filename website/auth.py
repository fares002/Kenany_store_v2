from flask import Blueprint, render_template, redirect, url_for, flash
from .forms import SignUpForm, LoginForm, PasswordChangeForm, RequestResetForm, ResetPasswordForm
from .models import Customer
from . import db, mail, app
from flask_login import login_user, logout_user, login_required, current_user
from flask_mail import Message
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from datetime import datetime


auth = Blueprint('auth', __name__)




@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    """
    Register a new customer account.

    This function handles the registration process for a new customer account.
    It validates the form data, creates a new customer object, and saves it to the database.

    Returns:
        A rendered template for the registration page.

    """
    form = SignUpForm()
    
    if form.validate_on_submit():
        email = form.email.data
        username = form.username.data
        phone_number = form.phone_number.data
        address = form.address.data
        password = form.password.data
        confirm_password = form.confirm_password.data
        
        if password == confirm_password:
            new_customer = Customer()
            new_customer.email = email
            new_customer.username = username
            new_customer.phone_number = phone_number
            new_customer.address = address
            new_customer.password = confirm_password
            
            try:
                db.session.add(new_customer)
                db.session.commit()
                flash('Account created successfully!', 'success')
                return redirect(url_for('auth.login'))
            except Exception as e:
                print(e)
                flash('Account Not created!, Email already exists', 'danger')
            
            form.email.data = ''
            form.username.data = ''
            form.password.data = ''
            form.confirm_password.data = ''
            
            
    return render_template('register.html', form=form)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    """
    Handle the login functionality.

    This function validates the login form submitted by the user. If the form is valid,
    it checks if the provided email exists in the database and if the password is correct.
    If the login is successful, the user is redirected to the home page. Otherwise, an
    appropriate error message is flashed and the login page is rendered again.

    Returns:
        The rendered login template with the login form.
    """
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        
        customer = Customer.query.filter_by(email=email).first()
        
        if customer:
            if customer.verify_password(password):
                flash('Login Successful!', 'success')
                login_user(customer)
                return redirect(url_for('views.home'))
            else:
                flash('Invalid Email or Password', 'danger')
        else:
            flash('Invalid Email or Password', 'danger')
    
    return render_template('login.html', form=form)
     

@auth.route('/logout', methods=['GET', 'POST'])
@login_required
def log_out():
    """
    Logs out the user and redirects to the home page.

    Returns:
        A redirect response to the home page.
    """
    logout_user()
    return redirect(url_for('views.home'))


@auth.route('/profile/<int:id>', methods=['GET', 'POST'])
@login_required
def profile(id):
    """
    Render the profile page for a given customer ID.

    Args:
        id (int): The ID of the customer.

    Returns:
        str: The rendered HTML template for the profile page.
    """
    customer = Customer.query.get(id)
    date_string = customer.date_joined
        
    formatted_date = date_string.strftime("%B %d, %Y, %H:%M")
 
    return render_template('profile.html', customer=customer , date_object=formatted_date)




@auth.route('/change_password/<int:id>', methods=['GET', 'POST'])
@login_required
def change_password(id):
    """
    Change the password for a customer.

    Args:
        id (int): The ID of the customer.

    Returns:
        The rendered template for the change password page.

    """
    form = PasswordChangeForm()
    customer = Customer.query.get(id)
    if form.validate_on_submit():
        current_password = form.Current_Password.data
        new_password = form.New_Password.data
        confirm_new_password = form.Confirm_New_Password.data
        if new_password == confirm_new_password:
            if customer.verify_password(current_password):
                customer.password = new_password
                db.session.commit()
                flash('Password Changed Successfully!', 'success')
                return redirect(url_for('auth.profile', id=customer.id))
            else:
                flash('Invalid Current Password', 'danger')
        else:
            flash("Passwords don't match!", 'danger')
            
    return render_template('change_password.html', form=form)




def send_rest_email(customer):
    """
    Sends a password reset email to the specified customer.

    Args:
        customer: The customer object representing the recipient of the email.

    Returns:
        None
    """
    token = customer.get_reset_token()
    msg = Message('Password Reset Request',sender='faresosama002@gmail.com', recipients=[customer.email])
    msg.body = f'''To reset your password, visit the following link:
{url_for('auth.reset_token', token=token, _external=True)}
if you did not make this request then simply ignore this email and no changes will be made.    
'''
    mail.send(msg)




@auth.route('/reset_password', methods=['GET', 'POST'])
def reset_request():
    """
    Handle the reset password request.

    If the user is already authenticated, redirect them to the home page.
    Otherwise, display the reset password form.
    If the form is submitted and valid, send a reset password email to the user.
    If the email exists in the database, display a success message and redirect to the login page.
    If the email does not exist, display an error message.
    """
    
    if current_user.is_authenticated:
        return redirect(url_for('views.home'))  
    form = RequestResetForm()
    if form.validate_on_submit():
        email = form.email.data
        customer = Customer.query.filter_by(email=email).first()
        if customer:
            send_rest_email(customer)
            flash('An email has been sent with instructions to reset your password', 'info')
            return redirect(url_for('auth.login'))
        else:
            flash('Email does not exist', 'danger')
    return render_template('reset_request.html', title='Reset Password', form=form)



@auth.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_token(token):
    """
    Reset the user's password using the provided token.

    Args:
        token (str): The reset token for the user.

    Returns:
        A redirect response if the token is invalid or expired, or if the user is already authenticated.
        Otherwise, renders the reset_token.html template with the reset password form.

    Raises:
        SQLAlchemyError: If an error occurs while updating the user's password in the database.
    """
    if current_user.is_authenticated:
        return redirect(url_for('views.home'))
    user = Customer.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('auth.reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        try:
            user.password = form.Confirm_New_Password.data
            db.session.commit()
            flash('Your password has been updated! You are now able to log in with your new password', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            print(e)
            flash('Something went wrong', 'danger')
            return redirect(url_for('auth.reset_request'))
        except SQLAlchemyError as s:
            print(s)
            flash('Something went wrong', 'danger')
            return redirect(url_for('auth.reset_request'))
    return render_template('reset_token.html', title='Reset Password', form=form)