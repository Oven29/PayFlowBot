from .check import router as check_router
from .participants import router as participants_router

routers = (
    check_router,
    participants_router,
)
