from fastapi import APIRouter, Depends, Query

from app.api.dependencies.auth_dependencies import get_current_user
from app.api.dependencies.order_dependencies import get_order_service
from app.models.models import UsersTable
from app.schemas.order import OrderListResponse, OrderResponse
from app.services.order_service import OrderService

router = APIRouter(prefix="/api/v5.0", tags=["Orders"])

# ========================================================
#                   CART ROUTES
# ========================================================


@router.post("/orders", status_code=201, response_model=OrderResponse)
def create_order_route(
    order_service: OrderService = Depends(get_order_service),  # noqa: B008
    current_user: UsersTable = Depends(get_current_user),  # noqa: B008
) -> OrderResponse:

    # here we add de paymente logic we sent the payment to stripe etc etc,however
    # this is just a project so we dont have payment service

    return order_service.create_order(user_id=current_user.id)


@router.get("/orders", status_code=200, response_model=OrderListResponse)
def get_orders_route(
    order_service: OrderService = Depends(get_order_service),  # noqa: B008
    current_user: UsersTable = Depends(get_current_user),  # noqa: B008
    page: int = Query(1, ge=1, description="page number"),
    page_size: int = Query(10, ge=10, le=50, description="page size"),
) -> OrderListResponse:
    orders = order_service.get_user_orders(
        user_id=current_user.id, page=page, page_size=page_size
    )
    return OrderListResponse.model_validate({"orders": orders})


@router.get("/orders/{order_id}", status_code=200, response_model=OrderResponse)
def get_order_route(
    order_id: int,
    order_service: OrderService = Depends(get_order_service),  # noqa: B008
    current_user: UsersTable = Depends(get_current_user),  # noqa: B008
) -> OrderResponse:

    return order_service.get_order(user_id=current_user.id, order_id=order_id)
