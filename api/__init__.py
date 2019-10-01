from .cloudflare import main
from .curl import get, post, patch, put, delete
__all__ = [ "cloudflare", "curl" ]