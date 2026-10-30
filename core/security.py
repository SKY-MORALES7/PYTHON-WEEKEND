import logging
import time
from django.conf import settings
from django.core.cache import cache
from django.core.signing import BadSignature, SignatureExpired, dumps, loads

logger = logging.getLogger(__name__)

FORM_TIMESTAMP_SALT = "pw-anti-bot-ts"


def is_email_sending_enabled():
    """
    Global kill-switch for outbound emails.
    Can be toggled via EMAIL_ENABLED in environment variables or settings.py.
    """
    return getattr(settings, "EMAIL_ENABLED", True)


def get_client_ip(request):
    """
    Safely retrieves the client's IP address, accounting for reverse proxies
    such as Cloudflare, Render, Nginx, or Heroku.
    """
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        # First IP in the comma-separated list is the actual client
        ip = x_forwarded_for.split(",")[0].strip()
    else:
        ip = request.META.get("REMOTE_ADDR", "127.0.0.1")
    return ip


def generate_form_timestamp():
    """
    Generates a cryptographically signed timestamp token when a form is rendered.
    Used to detect bots that submit forms impossibly fast (< min_seconds) or
    replay direct POST requests without loading the form page.
    """
    return dumps(time.time(), salt=FORM_TIMESTAMP_SALT)


def validate_form_timestamp(request, field_name="form_ts", min_seconds=2.5, max_age=7200):
    """
    Validates the signed timestamp token submitted with a POST form.
    - Returns False if the token is missing, tampered with, expired, or submitted
      faster than `min_seconds` (typical for automated spam bots).
    """
    if getattr(settings, "DEBUG", False) and not getattr(settings, "TESTING_HONEYPOT", False):
        # Still validate if token is present, but allow fast local test client posts without token
        token = request.POST.get(field_name, "").strip()
        if not token:
            return True

    token = request.POST.get(field_name, "").strip()
    if not token:
        logger.warning(f"Missing form timestamp token '{field_name}' from IP {get_client_ip(request)}.")
        return False

    try:
        rendered_at = float(loads(token, salt=FORM_TIMESTAMP_SALT, max_age=max_age))
    except (BadSignature, SignatureExpired, ValueError, TypeError) as exc:
        logger.warning(f"Invalid/expired form timestamp token from IP {get_client_ip(request)}: {exc}")
        return False

    elapsed = time.time() - rendered_at
    if elapsed < min_seconds:
        logger.warning(
            f"Bot speed trap triggered by IP {get_client_ip(request)}: "
            f"submitted in {elapsed:.2f}s (min {min_seconds}s)."
        )
        return False

    return True


def validate_honeypot(request, field_name="website"):
    """
    Checks if hidden honeypot decoy field(s) were filled out.
    - Real humans: cannot see the field, so it remains empty -> returns True (safe).
    - Bots: automatically populate every input -> returns False (flagged as bot).
    """
    decoy_fields = [field_name, "company_url", "phone_number_ext"]
    for fname in decoy_fields:
        honeypot_value = request.POST.get(fname, "").strip()
        if honeypot_value:
            logger.warning(
                f"Honeypot triggered on field '{fname}' by IP {get_client_ip(request)}. "
                f"Value: '{honeypot_value[:50]}'"
            )
            return False
    return True


def check_rate_limit(request, action, max_requests=5, window_seconds=600):
    """
    Rate limiter using Django's built-in cache framework.
    - Staff / superusers are 100% EXEMPT from rate limits (never locked out).
    - If DEBUG=True (local dev), rate limiting is disabled.
    - For anonymous visitors: allows up to `max_requests` per `window_seconds`.
    
    Returns:
        (is_allowed: bool, remaining_seconds: int)
    """
    # 1. Always exempt authenticated staff and superusers
    if getattr(request, "user", None) and request.user.is_authenticated and request.user.is_staff:
        return True, 0

    # 2. Disable in debug mode to facilitate easy local testing
    if getattr(settings, "DEBUG", False) and not getattr(settings, "TESTING_RATE_LIMIT", False):
        return True, 0

    client_ip = get_client_ip(request)
    cache_key = f"ratelimit:{action}:{client_ip}"

    current_requests = cache.get(cache_key, 0)
    if current_requests >= max_requests:
        logger.warning(
            f"Rate limit exceeded for action '{action}' by IP {client_ip} "
            f"({current_requests}/{max_requests} requests)"
        )
        return False, window_seconds

    # Increment request count and set window
    try:
        if current_requests == 0:
            cache.set(cache_key, 1, timeout=window_seconds)
        else:
            cache.incr(cache_key)
    except Exception as e:
        # Fallback in case cache backend has a hiccup — fail open to not break legitimate users
        logger.error(f"Rate limiter cache error: {e}")
        return True, 0

    return True, 0
