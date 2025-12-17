"""
MetaPersona - Identity Layer
Handles cryptographic identity, profile encryption, and secure storage.
"""
import os
import json
from pathlib import Path
from datetime import datetime
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64


class IdentityLayer:
    """Manages user identity with keypair and encrypted profile storage."""
    
    def __init__(self, data_dir: str = "./data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.private_key_path = self.data_dir / "private_key.pem"
        self.public_key_path = self.data_dir / "public_key.pem"
        self.identity_path = self.data_dir / "identity.json"
        
    def generate_keypair(self, passphrase: str = None) -> dict:
        """Generate RSA keypair for user identity."""
        print("🔐 Generating cryptographic identity...")
        
        # Generate private key
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )
        
        # Serialize private key
        encryption_algorithm = serialization.NoEncryption()
        if passphrase:
            encryption_algorithm = serialization.BestAvailableEncryption(
                passphrase.encode()
            )
        
        pem_private = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=encryption_algorithm
        )
        
        # Generate and serialize public key
        public_key = private_key.public_key()
        pem_public = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        
        # Save keys
        self.private_key_path.write_bytes(pem_private)
        self.public_key_path.write_bytes(pem_public)
        
        # Create identity metadata
        identity = {
            "created_at": datetime.now().isoformat(),
            "public_key_fingerprint": self._get_fingerprint(pem_public),
            "version": "1.0"
        }
        
        self.identity_path.write_text(json.dumps(identity, indent=2))
        
        print(f"✓ Identity created with fingerprint: {identity['public_key_fingerprint'][:16]}...")
        return identity
    
    def _get_fingerprint(self, public_key_bytes: bytes) -> str:
        """Generate fingerprint from public key."""
        digest = hashes.Hash(hashes.SHA256(), backend=default_backend())
        digest.update(public_key_bytes)
        return base64.b64encode(digest.finalize()).decode()
    
    def load_private_key(self, passphrase: str = None):
        """Load private key from storage."""
        if not self.private_key_path.exists():
            raise FileNotFoundError("Private key not found. Generate identity first.")
        
        password = passphrase.encode() if passphrase else None
        return serialization.load_pem_private_key(
            self.private_key_path.read_bytes(),
            password=password,
            backend=default_backend()
        )
    
    def load_public_key(self):
        """Load public key from storage."""
        if not self.public_key_path.exists():
            raise FileNotFoundError("Public key not found. Generate identity first.")
        
        return serialization.load_pem_public_key(
            self.public_key_path.read_bytes(),
            backend=default_backend()
        )
    
    def encrypt_data(self, data: str, passphrase: str) -> bytes:
        """Encrypt data using AES-256."""
        # Derive key from passphrase
        salt = os.urandom(16)
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        key = kdf.derive(passphrase.encode())
        
        # Encrypt data
        iv = os.urandom(16)
        cipher = Cipher(
            algorithms.AES(key),
            modes.CBC(iv),
            backend=default_backend()
        )
        encryptor = cipher.encryptor()
        
        # Pad data to block size
        padding_length = 16 - (len(data.encode()) % 16)
        padded_data = data.encode() + bytes([padding_length] * padding_length)
        
        ciphertext = encryptor.update(padded_data) + encryptor.finalize()
        
        # Return salt + iv + ciphertext
        return salt + iv + ciphertext
    
    def decrypt_data(self, encrypted_data: bytes, passphrase: str) -> str:
        """Decrypt data using AES-256."""
        # Extract components
        salt = encrypted_data[:16]
        iv = encrypted_data[16:32]
        ciphertext = encrypted_data[32:]
        
        # Derive key
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        key = kdf.derive(passphrase.encode())
        
        # Decrypt
        cipher = Cipher(
            algorithms.AES(key),
            modes.CBC(iv),
            backend=default_backend()
        )
        decryptor = cipher.decryptor()
        padded_data = decryptor.update(ciphertext) + decryptor.finalize()
        
        # Remove padding
        padding_length = padded_data[-1]
        data = padded_data[:-padding_length]
        
        return data.decode()
    
    def identity_exists(self) -> bool:
        """Check if identity already exists."""
        return (self.private_key_path.exists() and 
                self.public_key_path.exists() and 
                self.identity_path.exists())
    
    def get_identity_info(self) -> dict:
        """Get identity information."""
        if not self.identity_path.exists():
            return None
        return json.loads(self.identity_path.read_text())
