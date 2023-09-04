import string
import random


def get_random_string() -> str:
	return ''.join(random.choices(string.ascii_lowercase, k=10))


def get_random_email() -> str:
	return f"{get_random_string()}@gmail.com"


def get_random_password() -> str:
	return get_random_string()
