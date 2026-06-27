from decimal import Decimal

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Expense, Group

User = get_user_model()


class DivideAiApiTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user("joao", "joao@example.com", "SenhaForte123")
        self.other = User.objects.create_user("maria", "maria@example.com", "SenhaForte123")

    def authenticate(self, user):
        self.client.force_authenticate(user=user)

    def test_register_and_protected_endpoint(self):
        response = self.client.post(
            "/api/auth/register/",
            {
                "username": "ana",
                "email": "ana@example.com",
                "password": "SenhaForte123",
                "password_confirm": "SenhaForte123",
            },
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        response = self.client.get("/api/groups/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_group_list_is_scoped_by_member(self):
        group = Group.objects.create(name="Viagem", owner=self.user)
        group.members.add(self.user)
        other_group = Group.objects.create(name="Casa", owner=self.other)
        other_group.members.add(self.other)

        self.authenticate(self.user)
        response = self.client.get("/api/groups/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["id"], group.id)

    def test_expense_and_balance(self):
        group = Group.objects.create(name="Viagem", owner=self.user)
        group.members.add(self.user, self.other)
        expense = Expense.objects.create(
            group=group,
            title="Jantar",
            amount=Decimal("300.00"),
            paid_by=self.user,
        )
        expense.participants.add(self.user, self.other)

        self.authenticate(self.user)
        response = self.client.get(f"/api/groups/{group.id}/balances/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["settlements"][0]["from_user"], "maria")
        self.assertEqual(response.data["settlements"][0]["to_user"], "joao")
        self.assertEqual(response.data["settlements"][0]["amount"], 150.0)
