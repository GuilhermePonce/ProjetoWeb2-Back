from django.contrib import admin

from .models import Expense, Group


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ("name", "owner", "created_at")
    search_fields = ("name", "owner__username")
    filter_horizontal = ("members",)


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ("title", "group", "amount", "paid_by", "created_at")
    search_fields = ("title", "group__name", "paid_by__username")
    filter_horizontal = ("participants",)
