"""
Encryption utilities for secure session storage
Uses AES-256 encryption with PBKDF2 key derivation
"""
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
import os
import base64
import json

class EncryptionManager:
    def __init__(self):
        self.backend = default_backend()
        self.iterations = 100000  # PBKDF2 iterations
    
    def derive_key(self, password: str, salt: bytes) -> bytes:
        """Derive encryption key from password using PBKDF2"""
        kdf = PBKDF2(
            algorithm=hashes.SHA256(),
            length=32,  # 256 bits for AES-256
            salt=salt,
            iterations=self.iterations,
            backend=self.backend
        )
        return kdf.derive(password.encode())
    
    def encrypt(self, data: str, password: str) -> str:
        """Encrypt data with password"""
        # Generate random salt and IV
        salt = os.urandom(16)
        iv = os.urandom(16)
        
        # Derive key from password
        key = self.derive_key(password, salt)
        
        # Create cipher
        cipher = Cipher(
            algorithms.AES(key),
            modes.CBC(iv),
            backend=self.backend
        )
        encryptor = cipher.encryptor()
        
        # Pad data to block size (16 bytes for AES)
        padded_data = self._pad(data.encode())
        
        # Encrypt
        ciphertext = encryptor.update(padded_data) + encryptor.finalize()
        
        # Combine salt + IV + ciphertext and encode
        encrypted = salt + iv + ciphertext
        return base64.b64encode(encrypted).decode('utf-8')
    
    def decrypt(self, encrypted_data: str, password: str) -> str:
        """Decrypt data with password"""
        try:
            # Decode from base64
            encrypted = base64.b64decode(encrypted_data.encode('utf-8'))
            
            # Extract salt, IV, and ciphertext
            salt = encrypted[:16]
            iv = encrypted[16:32]
            ciphertext = encrypted[32:]
            
            # Derive key from password
            key = self.derive_key(password, salt)
            
            # Create cipher
            cipher = Cipher(
                algorithms.AES(key),
                modes.CBC(iv),
                backend=self.backend
            )
            decryptor = cipher.decryptor()
            
            # Decrypt
            padded_data = decryptor.update(ciphertext) + decryptor.finalize()
            
            # Unpad
            data = self._unpad(padded_data)
            return data.decode('utf-8')
        except Exception as e:
            raise ValueError(f"Decryption failed: {str(e)}")
    
    def _pad(self, data: bytes) -> bytes:
        """PKCS7 padding"""
        block_size = 16
        padding_length = block_size - (len(data) % block_size)
        padding = bytes([padding_length] * padding_length)
        return data + padding
    
    def _unpad(self, data: bytes) -> bytes:
        """Remove PKCS7 padding"""
        padding_length = data[-1]
        return data[:-padding_length]
    
    def encrypt_json(self, data: dict, password: str) -> str:
        """Encrypt JSON data"""
        json_str = json.dumps(data)
        return self.encrypt(json_str, password)
    
    def decrypt_json(self, encrypted_data: str, password: str) -> dict:
        """Decrypt JSON data"""
        json_str = self.decrypt(encrypted_data, password)
        return json.loads(json_str)
