
from .auth import auth_router, auth_api_router
from .posts import posts_router, posts_api_router
from .users import router as users_router
from .comments import router as comments_router

__all__ = [
    "auth_router", 
    "auth_api_router", 
    "posts_router", 
    "posts_api_router", 
    "users_router", 
    "comments_router"
]
