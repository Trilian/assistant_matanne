"""Script pour générer des clés VAPID pour les notifications push."""
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
import base64

# Générer une paire de clés EC P-256
private_key = ec.generate_private_key(ec.SECP256R1(), default_backend())

# Extraire la clé privée (32 bytes)
private_numbers = private_key.private_numbers()
private_bytes = private_numbers.private_value.to_bytes(32, byteorder='big')
private_b64 = base64.urlsafe_b64encode(private_bytes).decode('utf-8').rstrip('=')

# Extraire la clé publique (format non compressé: 04 + X + Y = 65 bytes)
public_key = private_key.public_key()
public_numbers = public_key.public_numbers()
x_bytes = public_numbers.x.to_bytes(32, byteorder='big')
y_bytes = public_numbers.y.to_bytes(32, byteorder='big')
public_bytes = b'\x04' + x_bytes + y_bytes
public_b64 = base64.urlsafe_b64encode(public_bytes).decode('utf-8').rstrip('=')

print("=" * 60)
print("CLÉS VAPID GÉNÉRÉES")
print("=" * 60)
print()
print("Ajoutez ces lignes dans votre .env.local :")
print()
print(f"VAPID_PUBLIC_KEY={public_b64}")
print(f"VAPID_PRIVATE_KEY={private_b64}")
print()
print("=" * 60)
