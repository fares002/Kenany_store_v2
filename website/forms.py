from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, FloatField ,PasswordField, SubmitField, BooleanField, EmailField, SelectField, FileField
from wtforms.validators import Length, EqualTo, Email, DataRequired, ValidationError, NumberRange  , Optional
from flask_wtf.file import FileField 
from .models import Customer

class SignUpForm(FlaskForm):
    """
    Form for user sign up.
    
    Attributes:
        username (StringField): Field for entering the username.
        email (EmailField): Field for entering the email.
        password (PasswordField): Field for entering the password.
        confirm_password (PasswordField): Field for confirming the password.
        phone_number (StringField): Field for entering the phone number.
        address (StringField): Field for entering the address.
        submit (SubmitField): Button for submitting the form.
    """
    
    username = StringField(label='Username', validators=[Length(min=2, max=30), DataRequired()])
    email = EmailField(label='Email', validators=[Email(), DataRequired()])
    password = PasswordField(label='Password', validators=[Length(min=6), DataRequired()])
    confirm_password = PasswordField(label='Confirm Password', validators=[EqualTo('password'), DataRequired()])
    phone_number = StringField(label='Phone Number', validators=[DataRequired(),Length(min=10, max=15, message='Phone number must be between 10 and 15 characters')])
    address = StringField(label='Address', validators=[DataRequired()])
    submit = SubmitField(label='Sign Up')

    
    
class LoginForm(FlaskForm):
    """
    Represents a login form.

    Attributes:
        email (EmailField): The email field for the login form.
        password (PasswordField): The password field for the login form.
        remember (BooleanField): The remember me checkbox for the login form.
        submit (SubmitField): The submit button for the login form.
    """
    
    email= EmailField(label='Email', validators=[Email(), DataRequired()])
    password = PasswordField(label='Password', validators=[DataRequired()])
    remember = BooleanField(label='Remember Me')
    submit = SubmitField(label='Login')
    
    
    
class PasswordChangeForm(FlaskForm):
    """
    Form for changing the user's password.

    Attributes:
        Current_Password (PasswordField): Field for entering the current password.
        New_Password (PasswordField): Field for entering the new password.
        Confirm_New_Password (PasswordField): Field for confirming the new password.
        submit (SubmitField): Button for submitting the form.
    """
    
    Current_Password=PasswordField(label='Current Password' , validators=[DataRequired(), Length(min=6)])
    New_Password=PasswordField(label='New_Password' , validators=[DataRequired(), Length(min=6)])
    Confirm_New_Password=PasswordField(label='Confirm_New_Password' , validators=[DataRequired(), EqualTo('New_Password'), Length(min=6)])
    submit = SubmitField(label='Change Password')
    
    
    
class ShopItemsForm(FlaskForm):
    """
    Form for adding or updating shop items.
    """

    product_name = StringField('Name of Product', validators=[DataRequired()])
    current_price = FloatField('Current Price', validators=[DataRequired()])
    previous_price = FloatField('Previous Price', validators=[Optional()])
    in_stock = IntegerField('In Stock', validators=[DataRequired(), NumberRange(min=0)])
    product_picture = FileField('Product Picture', validators=[DataRequired()])
    description = StringField('Description')
    flash_sale = BooleanField('Flash Sale')
    featured_product = BooleanField('Featured Product')

    add_product = SubmitField('Add Product')
    update_product = SubmitField('Update')
    
    
    
class OrdersForm(FlaskForm):
    """
    A form class for updating the status of an order.

    Attributes:
        order_status (SelectField): A dropdown field for selecting the order status.
        submit (SubmitField): A button for submitting the form.
    """
    order_status = SelectField('Order Status', choices=[('Pending', 'Pending'), ('Accepted', 'Accepted'), ('Out for delivery', 'Out for delivery'), ('Delivered', 'Delivered'), ('Cancelled', 'Cancelled')])
    submit = SubmitField('Update status')
    


class CategoryForm(FlaskForm):
    """
    A form class for managing category selection and order status update.

    Attributes:
        order_status (SelectField): The field for selecting the category.
        submit (SubmitField): The field for submitting the form.

    """
    category = SelectField('Category', choices=[('Smartphones', 'Smartphones'), ('Headphones and Speakers', 'Headphones and Speakers'), ('Laptops', 'Laptops'), ('Accessories', 'Accessories')])
    submit = SubmitField('Update status')
    
    
    
class RequestResetForm(FlaskForm):
    """
    Form for requesting a password reset.
    """

    email = EmailField(label='Email', validators=[Email(), DataRequired()])
    submit = SubmitField(label='Request Password Reset')
    
    def validate_email(self, email):
        """
        Validate the email field.

        Parameters:
        - email: The email address to validate.

        Raises:
        - ValidationError: If there is no account with the provided email.
        """
        customer = Customer.query.filter_by(email=email.data).first()
        if customer is None:
            raise ValidationError('There is no account with that email. You must register first.')
        
        
        
class ResetPasswordForm(FlaskForm):
    """
    A form used for resetting a user's password.

    Attributes:
        New_Password (PasswordField): The field for entering the new password.
        Confirm_New_Password (PasswordField): The field for confirming the new password.
        submit (SubmitField): The button for submitting the form.
    """
    
    New_Password=PasswordField(label='New_Password' , validators=[DataRequired(), Length(min=6)])
    Confirm_New_Password=PasswordField(label='Confirm_New_Password' , validators=[DataRequired(), EqualTo('New_Password'), Length(min=6)])
    submit = SubmitField(label='Reset Password')