from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


class Group(models.Model):
    name = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="owned_groups",
        on_delete=models.CASCADE,
    )
    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="expense_groups",
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.name


class Expense(models.Model):
    group = models.ForeignKey(Group, related_name="expenses", on_delete=models.CASCADE)
    title = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    paid_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="paid_expenses",
        on_delete=models.PROTECT,
    )
    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="shared_expenses",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} - {self.amount}"

    def clean(self):
        if self.amount <= 0:
            raise ValidationError({"amount": "O valor da despesa deve ser maior que zero."})
        if self.group_id and self.paid_by_id:
            if not self.group.members.filter(id=self.paid_by_id).exists():
                raise ValidationError({"paid_by": "O pagador deve ser membro do grupo."})
