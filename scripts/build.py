import re
import os
import random
import string
import json
import pyzipper
import tempfile
import shutil
import pathlib
import hashlib

from datetime import datetime
from collections import defaultdict
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

def generate_random_password(length=32):
    """Generate a random password of given length."""
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))


def hash_512(data: bytes) -> bytes:
    return hashlib.sha512(data).digest()

def encrypt_aes(data: bytes, key: bytes) -> bytes:
    iv = hash_512(key)[:16]
    cipher = AES.new(key, AES.MODE_CBC, iv)
    ct_bytes = cipher.encrypt(pad(data, AES.block_size))
    return ct_bytes

def decrypt_aes(data: bytes, key: bytes) -> bytes:
    iv = hash_512(key)[:16]
    cipher = AES.new(key, AES.MODE_CBC, iv)
    pt = cipher.decrypt(data)
    return unpad(pt, AES.block_size)

def protect_zip(source_path, target_directory, record_directory, password):
    """Protect a ZIP file by placing it inside a new password-protected ZIP file."""
    filename = os.path.basename(source_path)
    protected_zip_path = os.path.join(target_directory, "archive.dump")
    protected_password_path = os.path.join(target_directory, "archive.log.txt")
    version_file_path = os.path.join(record_directory, "version_hash.txt")

    os.makedirs(record_directory, exist_ok=True)
    os.makedirs(target_directory, exist_ok=True)
    log_data = {
        "name":  filename,
        "file_path": protected_zip_path.replace("\\","/"),
        "password": password.decode('utf8')
    }
    
    with open(source_path, 'rb') as f:
        content = f.read()
        enc = encrypt_aes(content, password)
        hex = hash_512(enc).hex()
        with open(protected_zip_path, 'wb') as f_write:
            f_write.write(enc)    
        with open(protected_password_path, 'w') as f_write:
            f_write.write(json.dumps(log_data, ensure_ascii=False, indent=4))
        with open(version_file_path, 'w') as f_write:
            f_write.write(hex)
    return True

        
def process_directory(source_directory, target_directory, record_directory):
    """Recursively search for ZIP files, protect them, and add to archive."""
    version_pattern = re.compile(r"^v(\d+\.)+(\d+$)")
    def is_single_zip_file(file_list):
        return len(file_list) == 1 and file_list[0].lower().endswith('.zip')
    def is_version_at_end(source_directory):
        return version_pattern.match(source_directory.split("\\")[-1]) is not None
    def is_match_project(x):
        return is_version_at_end(x[0]) and is_single_zip_file(x[2])
    def split_version(source_directory):
        return str(pathlib.Path(source_directory).parent), source_directory.split("\\")[-1]
    def make_path_version(x):
        return (*split_version(x[0]), x[2][0])
        
    project_map = defaultdict(list)
    matches = filter(is_match_project, os.walk(source_directory))
    matches = map(make_path_version, matches)
    for project_name, version, file_name in matches:
        project_map[project_name].append((version, file_name))
    
    results = []
    for project_path, version_lists in project_map.items():
        #target_version = sorted(version_lists, key=lambda x:x[0])[-1]
        for target_version in version_lists:
            password = generate_random_password().encode('utf8')
            source_path = os.path.join(project_path, target_version[0], target_version[1])
            archive_path = os.path.relpath(project_path, source_directory)
            archive_path = os.path.join(target_directory, archive_path, target_version[0])
            version_record_target = os.path.relpath(project_path, source_directory)
            version_record_target = os.path.join(record_directory, version_record_target, target_version[0])
            if os.path.isfile(os.path.join(version_record_target, "version.txt")):
                continue
            protect_zip(source_path, archive_path, version_record_target, password)
            print(f"Protected and archived {source_path}")
    return results

    
# Example usage
if __name__ == "__main__":
    source_directory = "source_archives"
    target_directory = "bin/archives"
    record_directory = "version"

    # Ensure target directory exists
    os.makedirs(target_directory, exist_ok=True)
    process_directory(source_directory, target_directory, record_directory)