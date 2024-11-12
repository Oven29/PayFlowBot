from .disputes import router as disputes_router
from .status import router as status_router
from .work import router as work_router

routers = (
    disputes_router,
    status_router,
    work_router,
)
