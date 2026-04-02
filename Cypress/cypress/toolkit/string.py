import random, string
import re

def random_string(length):
   letters = string.ascii_lowercase+string.ascii_uppercase+string.digits
   return ''.join(random.choice(letters) for i in range(length))


def sanitize_email_display_name(name):
    """
    Sanitize a string for use as an email display name (RFC 5322 compliant).
    Removes domain suffixes and special characters that cause validation failures.
    """
    # Remove common domain suffixes
    suffixes = ['.net', '.com', '.org', '.io', '.co', '.vip', '.app', '.dev']
    result = name
    for suffix in suffixes:
        result = re.sub(re.escape(suffix), '', result, flags=re.IGNORECASE)

    # Remove any remaining periods and other RFC 5322 special characters
    result = re.sub(r'[.<>@,;:\\\"\[\]()]', '', result)

    # Clean up any double spaces and strip
    result = re.sub(r'\s+', ' ', result).strip()

    return result