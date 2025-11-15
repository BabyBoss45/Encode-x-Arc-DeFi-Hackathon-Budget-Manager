import hmac
import hashlib
from typing import Optional


def verify_circle_signature(raw_body: bytes, header_signature: Optional[str], secret: str) -> bool:
    """
    Circle sends HMAC SHA256 hex digest in a header (name may vary).
    This function computes HMAC-SHA256(raw_body, secret) and compares to header_signature.
    """
    if not header_signature:
        return False
    computed = hmac.new(secret.encode("utf-8"), raw_body, hashlib.sha256).hexdigest()
    # Use hmac.compare_digest for timing-attack-resistant comparison
    return hmac.compare_digest(computed, header_signature)