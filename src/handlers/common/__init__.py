from .menu import router as menu_router
from .registered import router as registered_router

routers = (
    menu_router,
    registered_router,
)
