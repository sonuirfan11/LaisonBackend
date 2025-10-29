import random
import secrets
import string


def generate_otp():
    return ''.join(secrets.choice(string.digits) for _ in range(6))
