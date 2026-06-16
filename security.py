"""Pluggable signing utilities for IGoW.

Tries to use Ed25519 from `cryptography` when available. If not installed,
falls back to HMAC-SHA256 symmetric signatures (NOT public-key). The fallback
is provided for demo purposes only and should not be used in production.
"""
from typing import Tuple
import hashlib
import hmac

try:
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey
    from cryptography.hazmat.primitives import serialization
    HAS_CRYPTO = True
except Exception:
    HAS_CRYPTO = False


def generate_keypair() -> Tuple[bytes, bytes]:
    """Return (private, public) key pair bytes.

    If Ed25519 is available, returns raw private and public key bytes.
    Otherwise returns a symmetric HMAC key used for both sign/verify.
    """
    if HAS_CRYPTO:
        priv = Ed25519PrivateKey.generate()
        priv_bytes = priv.private_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PrivateFormat.Raw,
            encryption_algorithm=serialization.NoEncryption(),
        )
        pub = priv.public_key()
        pub_bytes = pub.public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw,
        )
        return priv_bytes, pub_bytes
    else:
        # Fallback: symmetric key
        key = hashlib.sha256(b"IGOW_DEMO_KEY").digest()
        return key, key


def sign(data: bytes, privkey: bytes) -> bytes:
    """Sign data and return signature bytes."""
    if HAS_CRYPTO:
        priv = Ed25519PrivateKey.from_private_bytes(privkey)
        return priv.sign(data)
    else:
        return hmac.new(privkey, data, hashlib.sha256).digest()


def verify(data: bytes, signature: bytes, pubkey: bytes) -> bool:
    """Verify signature; returns True if valid."""
    if HAS_CRYPTO:
        try:
            pub = Ed25519PublicKey.from_public_bytes(pubkey)
            pub.verify(signature, data)
            return True
        except Exception:
            return False
    else:
        expected = hmac.new(pubkey, data, hashlib.sha256).digest()
        return hmac.compare_digest(expected, signature)
