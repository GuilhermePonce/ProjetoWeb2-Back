from decimal import Decimal, ROUND_HALF_UP

from django.contrib.auth import get_user_model
from rest_framework import generics, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .models import Expense, Group
from .permissions import IsGroupMember
from .serializers import (
    ChangePasswordSerializer,
    ExpenseSerializer,
    GroupSerializer,
    LoginSerializer,
    PasswordResetSerializer,
    RegisterSerializer,
    UserSerializer,
)

User = get_user_model()
CENT = Decimal("0.01")


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]


class LoginView(TokenObtainPairView):
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]


class RefreshView(TokenRefreshView):
    permission_classes = [AllowAny]


class UserListView(generics.ListAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return User.objects.order_by("username")


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def me(request):
    return Response(UserSerializer(request.user).data)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def change_password(request):
    serializer = ChangePasswordSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    if not request.user.check_password(serializer.validated_data["old_password"]):
        return Response({"old_password": "Senha antiga incorreta."}, status=status.HTTP_400_BAD_REQUEST)
    request.user.set_password(serializer.validated_data["new_password"])
    request.user.save()
    return Response({"detail": "Senha alterada com sucesso."})


@api_view(["POST"])
@permission_classes([AllowAny])
def password_reset(request):
    serializer = PasswordResetSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    return Response(
        {
            "detail": (
                "Se o e-mail estiver cadastrado, um link de redefinicao "
                "sera enviado. No ambiente local esta acao e simulada."
            )
        }
    )


class GroupViewSet(viewsets.ModelViewSet):
    serializer_class = GroupSerializer
    permission_classes = [IsAuthenticated, IsGroupMember]

    def get_queryset(self):
        return Group.objects.filter(members=self.request.user).distinct()

    def perform_create(self, serializer):
        serializer.save()

    @action(detail=True, methods=["get"], url_path="balances")
    def balances(self, request, pk=None):
        group = self.get_object()
        members = list(group.members.all())
        paid = {user.id: Decimal("0.00") for user in members}
        owed = {user.id: Decimal("0.00") for user in members}

        expenses = group.expenses.prefetch_related("participants", "paid_by")
        total_expenses = Decimal("0.00")
        for expense in expenses:
            total_expenses += expense.amount
            paid[expense.paid_by_id] += expense.amount
            participants = list(expense.participants.all())
            if not participants:
                continue
            share = (expense.amount / Decimal(len(participants))).quantize(CENT, rounding=ROUND_HALF_UP)
            distributed = share * len(participants)
            remainder = expense.amount - distributed
            for index, participant in enumerate(participants):
                owed[participant.id] += share
                if index == 0:
                    owed[participant.id] += remainder

        balances = []
        creditors = []
        debtors = []
        for user in members:
            balance = (paid[user.id] - owed[user.id]).quantize(CENT)
            item = {
                "user": user.username,
                "user_id": user.id,
                "paid": float(paid[user.id].quantize(CENT)),
                "owed": float(owed[user.id].quantize(CENT)),
                "balance": float(balance),
            }
            balances.append(item)
            if balance > 0:
                creditors.append({"user": user, "amount": balance})
            elif balance < 0:
                debtors.append({"user": user, "amount": -balance})

        settlements = []
        creditor_index = 0
        debtor_index = 0
        while creditor_index < len(creditors) and debtor_index < len(debtors):
            creditor = creditors[creditor_index]
            debtor = debtors[debtor_index]
            amount = min(creditor["amount"], debtor["amount"]).quantize(CENT)
            if amount > 0:
                settlements.append(
                    {
                        "from_user": debtor["user"].username,
                        "to_user": creditor["user"].username,
                        "amount": float(amount),
                    }
                )
            creditor["amount"] -= amount
            debtor["amount"] -= amount
            if creditor["amount"] <= 0:
                creditor_index += 1
            if debtor["amount"] <= 0:
                debtor_index += 1

        return Response(
            {
                "group": group.name,
                "total_expenses": float(total_expenses.quantize(CENT)),
                "balances": balances,
                "settlements": settlements,
            }
        )


class ExpenseViewSet(viewsets.ModelViewSet):
    serializer_class = ExpenseSerializer
    permission_classes = [IsAuthenticated, IsGroupMember]

    def get_queryset(self):
        return (
            Expense.objects.filter(group__members=self.request.user)
            .select_related("group", "paid_by")
            .prefetch_related("participants")
            .distinct()
        )
