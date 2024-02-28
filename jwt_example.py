# import jwt
# from cryptography.hazmat.backends import default_backend
# from cryptography.hazmat.primitives import serialization
# from cryptography.hazmat.primitives.asymmetric import rsa

# private_key = rsa.generate_private_key(
#     public_exponent=65537,
#     key_size=2048,
#     backend=default_backend()
# )
# public_key = private_key.public_key()

# pem = public_key.public_bytes(
#     encoding=serialization.Encoding.PEM,
#     format=serialization.PublicFormat.SubjectPublicKeyInfo
# )


# data_to_encrypt = {'user_id': 123, 'role': 'admin'}
# encrypted_data = jwt.encode(data_to_encrypt, private_key, algorithm='RS256')

# print(encrypted_data)

# decoded_data = jwt.decode(encrypted_data, pem, algorithms=['RS256'])
# print(decoded_data)


import secrets

secret_key = secrets.token_hex(128)

print(secret_key)

import uuid
import random
import string
import hashlib
import time

def generate_error_code():
    timestamp = str(int(time.time()))
    random_letter = random.choice(string.ascii_uppercase)  # Случайная буква верхнего регистра
    random_part = ''.join(random.choices(string.ascii_lowercase + string.digits, k=5))  # 5 случайных символов из нижнего регистра и цифр
    error_id = hashlib.sha256((str(uuid.uuid4()) + timestamp + random_letter + random_part).encode()).hexdigest()[:12]
    return random_letter + ''.join(random.sample(error_id, len(error_id)))

# Пример использования:
error_code = generate_error_code()
print("Error Code:", error_code)
