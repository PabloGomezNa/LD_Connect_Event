
# We will use this to verify the webhook signature
import hashlib
import hmac

def verify_taiga_signature(request, secret):
    """
    Validates the Taiga HMAC-SHA1 signature on the incoming request.

    :param request: The Flask request object
    :param secret: The secret key as a string or bytes
    :return: Boolean, True if valid, False otherwise
    """
    # 1) Grab the signature from the header
    signature_header = request.headers.get("X-TAIGA-WEBHOOK-SIGNATURE", "")

    # 2) The raw request body, as bytes
    raw_body = request.data

    # 3) If your secret is a string, encode it to bytes
    if isinstance(secret, str):
        secret = secret.encode("utf-8")

    # 4) Re-compute the HMAC (sha1)
    mac = hmac.new(secret, msg=raw_body, digestmod=hashlib.sha1)
    expected_sig = mac.hexdigest()

    # 5) Compare them
    return hmac.compare_digest(expected_sig, signature_header)
