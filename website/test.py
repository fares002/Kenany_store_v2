# from intasend import APIService
from itsdangerous import URLSafeTimedSerializer as Serializer
from . import app

# API_PUBLISHABLE_KEY = "ISPubKey_test_8ff503c9-81b7-4144-88df-4ce1d65a3cdb"
# API_TOKEN = "ISSecretKey_test_2d424435-3893-4eb4-ae0f-e0a7e8736288"


# serevice = APIService(token=API_TOKEN, publishable_key=API_PUBLISHABLE_KEY, test=True)

# create_order = serevice.collect.mpesa_stk_push(phone_number="2541557636517", email="faresosama002@gmail.com", amount=100, currency="USD", narrative="Purchase of goods")

# print(create_order)

s = Serializer(app.config['SECRET_KEY'], expires_in=30)
token = s.dumps({'user_id':1}).encode('utf-8')
print(token)

try:
    decoded_data = s.loads(token, max_age=30)  # max_age is the expiration time in seconds
    print(f"Decoded Data: {decoded_data}")
except Exception as e:
    print(f"Error: {e}")