from ..routers.auth import router as auth_router
from ..routers.users import router as users_router
from ..routers.posts import router as posts_router
from ..routers.comments import router as comments_router

__all__ = ["auth_router", "users_router", "posts_router", "comments_router"]