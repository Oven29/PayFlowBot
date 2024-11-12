from .menu import router as menu_router
from .orders import router as orders_router
from .registered import router as registered_router

routers = (
    menu_router,
    orders_router,
    registered_router,
)
