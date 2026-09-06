from django.db import models
from users.models import User

# Create your models here.

class Monitor(models.Model):
    class HealthStatus(models.TextChoices):
        UNKNOWN = "UNKNOWN", "Unknown"
        UP = "UP", "Up "
        DEGRADED = "DEGRADED", "Degraded"
        DOWN = "DOWN", "Down"
        RECOVERED = "RECOVERED", "Recovered"

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="monitors",
    )

    name = models.CharField(max_length=255)
    url = models.URLField()
    interval_seconds = models.PositiveBigIntegerField(default=60)
    is_active = models.BooleanField(default=True)
    current_status = models.CharField(
        max_length=20,
        choices=HealthStatus.choices,
        default=HealthStatus.UNKNOWN,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self):
        return self.name