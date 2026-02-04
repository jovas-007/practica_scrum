"""
Backend de autenticación personalizado para soportar contraseñas hasheadas con bcrypt
"""
import bcrypt
from django.contrib.auth.hashers import BasePasswordHasher


class BcryptPasswordHasher(BasePasswordHasher):
    """
    Hasher personalizado para contraseñas bcrypt de Node.js
    Formato: $2b$10$... o $2a$10$...
    """
    algorithm = "bcrypt_node"
    
    def salt(self):
        return bcrypt.gensalt().decode('utf-8')
    
    def encode(self, password, salt):
        """Codificar contraseña con bcrypt"""
        if isinstance(password, str):
            password = password.encode('utf-8')
        if isinstance(salt, str):
            salt = salt.encode('utf-8')
        
        hashed = bcrypt.hashpw(password, salt)
        return hashed.decode('utf-8')
    
    def verify(self, password, encoded):
        """Verificar contraseña contra hash bcrypt"""
        if isinstance(password, str):
            password = password.encode('utf-8')
        if isinstance(encoded, str):
            encoded = encoded.encode('utf-8')
        
        try:
            return bcrypt.checkpw(password, encoded)
        except (ValueError, TypeError):
            return False
    
    def safe_summary(self, encoded):
        return {
            'algorithm': self.algorithm,
            'hash': encoded[:20] + '...',
        }
    
    def must_update(self, encoded):
        return False


def identify_hasher(encoded):
    """Identificar si es un hash bcrypt de Node.js"""
    if encoded.startswith('$2b$') or encoded.startswith('$2a$') or encoded.startswith('$2y$'):
        return BcryptPasswordHasher()
    return None
