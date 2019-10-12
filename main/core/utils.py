import hashlib


def get_file_hash(file_field):
    hash_method = hashlib.sha256()
    for line in file_field.open(mode='rb'):
        hash_method.update(line)
    return hash_method.hexdigest()
