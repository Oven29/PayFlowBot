from .orders import router as orders_router
from .participants import router as participants_router

routers = (
    orders_router,
    participants_router,
)
