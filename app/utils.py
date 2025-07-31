from app import bcrypt


def check_password(hash_password, password):
    return bcrypt.check_password_hash(hash_password, password)


def hash_password(password):
    return bcrypt.generate_password_hash(password)
