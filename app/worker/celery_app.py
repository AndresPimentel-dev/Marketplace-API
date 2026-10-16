from celery import Celery

# Configura Redis como broker y backend de resultados
# el broker es donde el worker recibira la tarea y el backend donde la dejara lista
# y hecha
celery_app = Celery(
    "nexus_worker",
    broker="redis://redis:6379/0",
    backend="redis://redis:6379/1",
    include=["app.tasks.reservation_task"],
)
# aqui se define como se comunicaran redis y fast api aqui se define que solo por json,
# solo aceptara jsoin y devolvera json
# y que el horario seara universarl sin importar si estan configuradas en zonas distintas
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)
