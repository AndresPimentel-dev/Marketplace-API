from pydantic import BaseModel, Field


class PaymentWebhookPayload(BaseModel):
    event_id: str = Field(
        ...,
        description="Unique ID of the webhook event for idempotency",
        min_length=1,
        max_length=100,
    )
    payment_id: str = Field(
        ...,
        description="Unique ID of the payment transaction",
        min_length=1,
        max_length=100,
    )
    order_id: int = Field(..., description="ID of the order being paid")
    status: str = Field(
        ...,
        description="Payment status: 'succeeded' or 'failed'",
        min_length=1,
        max_length=50,
    )
