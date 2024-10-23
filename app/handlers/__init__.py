from .user_private import user_private_router
from .user_group import user_group_router
from .admin_private import admin_router


ROUTERS = [
    user_private_router,
    user_group_router,
    admin_router,
]
