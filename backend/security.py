from cryptography.fernet import Fernet, InvalidToken
import base64

# The generation of the Fernet key (CREDENTIAL_ENCRYPTION_KEY from environment)
# is considered an operational setup step and should be done securely,
# e.g., by running `Fernet.generate_key().decode()` and storing that in the .env file.

def encrypt_data(data: str, key: str) -> str:
    """Encrypts a string using Fernet encryption with the given key."""
    if not key:
        raise ValueError("Encryption key cannot be empty.")
    try:
        # Key must be URL-safe base64-encoded bytes.
        # The key from .env should already be in this format.
        fernet_key = key.encode('utf-8')
        f = Fernet(fernet_key)
        encrypted_data_bytes = f.encrypt(data.encode('utf-8'))
        return encrypted_data_bytes.decode('utf-8') # Store as string
    except Exception as e:
        # In a real application, log this error to a secure logging system.
        print(f"Encryption error: {e}") # Basic print for subtask visibility
        # Re-raising as ValueError to provide a generic error message to the caller.
        raise ValueError("Failed to encrypt data.") from e

def decrypt_data(encrypted_data: str, key: str) -> str:
    """Decrypts an encrypted string using Fernet encryption with the given key."""
    if not key:
        raise ValueError("Decryption key cannot be empty.")
    try:
        # Key must be URL-safe base64-encoded bytes.
        fernet_key = key.encode('utf-8')
        f = Fernet(fernet_key)
        decrypted_data_bytes = f.decrypt(encrypted_data.encode('utf-8'))
        return decrypted_data_bytes.decode('utf-8')
    except InvalidToken:
        # This specific exception is important for incorrect key or tampered data.
        # In a real application, log this attempt.
        print("Decryption error: Invalid token or key.") # Basic print
        raise ValueError("Failed to decrypt data: Invalid token or key.")
    except Exception as e:
        # In a real application, log this error.
        print(f"Decryption error: {e}") # Basic print
        raise ValueError("Failed to decrypt data.") from e
