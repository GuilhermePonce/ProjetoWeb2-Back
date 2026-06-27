from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    ExpenseViewSet,
    GroupViewSet,
    LoginView,
    RefreshView,
    RegisterView,
    UserListView,
    change_password,
    me,
    password_reset,
)

router = DefaultRouter()
router.register("groups", GroupViewSet, basename="group")
router.register("expenses", ExpenseViewSet, basename="expense")

urlpatterns = [
    path("auth/register/", RegisterView.as_view(), name="register"),
    path("auth/login/", LoginView.as_view(), name="login"),
    path("auth/refresh/", RefreshView.as_view(), name="token-refresh"),
    path("auth/me/", me, name="me"),
    path("auth/change-password/", change_password, name="change-password"),
    path("auth/password-reset/", password_reset, name="password-reset"),
    path("users/", UserListView.as_view(), name="users"),
    path("", include(router.urls)),
]
