from django.db import models


class ItemManager(models.Manager):
    def get_queryset(self) -> models.QuerySet:
        return super().get_queryset().filter(is_deleted=False)
    def all(self) -> models.QuerySet:
        return super().all().filter(is_deleted=False)