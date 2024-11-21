from .menu import router as menu_router
from .orders import router as orders_router
from .participants import router as participants_router
from .registered import router as registered_router

routers = (
    menu_router,
    orders_router,
    participants_router,
    registered_router,
)
