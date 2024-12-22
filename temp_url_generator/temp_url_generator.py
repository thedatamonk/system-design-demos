import time
import hmac
import hashlib
import base64
from urllib.parse import urlencode, urlparse, parse_qs

SECRET_KEY = "my_secret_key"  # Replace with a secure, random secret key

def generate_time_limited_url(base_url, duration_seconds):
    """
    Generate a URL that is valid for a limited duration.

    :param base_url: The base URL to be secured.
    :param duration_seconds: The duration (in seconds) for which the URL will be valid.
    :return: A time-limited URL.
    """
    expiry_time = int(time.time() + duration_seconds)  # Expiry timestamp
    payload = f"{base_url}|{expiry_time}"
    
    # Generate HMAC signature
    signature = hmac.new(
        SECRET_KEY.encode(), payload.encode(), hashlib.sha256
    ).digest()

    encoded_payload = base64.urlsafe_b64encode(f"{expiry_time}|".encode() + signature).decode()


    # Encode the expiry time in the signature

    # Construct the URL with only the combined signature
    query_params = {
        "signature": encoded_payload
    }
    return f"{base_url}?{urlencode(query_params)}"

def validate_time_limited_url(url):
    """
    Validate a time-limited URL to ensure it is still valid.

    :param url: The URL to validate.
    :return: True if valid, False otherwise.
    """
    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query)

    if "signature" not in query_params:
        return False

    encoded_payload = query_params["signature"][0]

    # Decode the payload to extract expiry and signature
    # try:
    decoded_payload = base64.urlsafe_b64decode(encoded_payload)
    expiry_time_encoded, signature = decoded_payload.split(b"|", 1)
    expiry_time = int(expiry_time_encoded.decode())
    # signature = base64.urlsafe_b64decode(signature.encode())
    # except (ValueError, IndexError, base64.binascii.Error):
    #     return False

    # Check if the URL has expired
    if time.time() > expiry_time:
        return False

    # Validate the signature
    base_url = parsed_url._replace(query="").geturl()
    payload = f"{base_url}|{expiry_time}"
    expected_signature = hmac.new(
        SECRET_KEY.encode(), payload.encode(), hashlib.sha256
    ).digest()

    return hmac.compare_digest(expected_signature, signature)

# Example Usage
if __name__ == "__main__":
    # Generate a URL valid for 60 seconds
    url = generate_time_limited_url("https://example.com/resource", 60)
    print("Generated URL:", url)

    # Validate the URL
    is_valid = validate_time_limited_url(url)
    print("Is the URL valid?:", is_valid)

    # Wait for it to expire and validate again
    time.sleep(61)
    is_valid_after_expiry = validate_time_limited_url(url)
    print("Is the URL valid after expiry?:", is_valid_after_expiry)
