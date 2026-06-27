from decimal import Decimal

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import Expense, Group

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username", "email", "first_name", "last_name")


class LoginSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        identifier = attrs.get(self.username_field)
        if identifier and "@" in identifier:
            user = User.objects.filter(email__iexact=identifier).first()
            if user:
                attrs[self.username_field] = user.get_username()
        return super().validate(attrs)


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ("id", "username", "email", "password", "password_confirm")

    def validate(self, attrs):
        if attrs["password"] != attrs["password_confirm"]:
            raise serializers.ValidationError({"password_confirm": "As senhas nao conferem."})
        return attrs

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("Este e-mail ja esta em uso.")
        return value

    def create(self, validated_data):
        validated_data.pop("password_confirm")
        return User.objects.create_user(**validated_data)


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, validators=[validate_password])
    new_password_confirm = serializers.CharField(write_only=True)

    def validate(self, attrs):
        if attrs["new_password"] != attrs["new_password_confirm"]:
            raise serializers.ValidationError({"new_password_confirm": "As senhas nao conferem."})
        return attrs


class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()


class GroupSerializer(serializers.ModelSerializer):
    owner = UserSerializer(read_only=True)
    members = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        many=True,
        required=False,
    )
    member_details = UserSerializer(source="members", many=True, read_only=True)

    class Meta:
        model = Group
        fields = (
            "id",
            "name",
            "description",
            "owner",
            "members",
            "member_details",
            "created_at",
        )
        read_only_fields = ("id", "owner", "member_details", "created_at")

    def create(self, validated_data):
        request = self.context["request"]
        members = validated_data.pop("members", [])
        group = Group.objects.create(owner=request.user, **validated_data)
        group.members.set(set([request.user, *members]))
        return group

    def update(self, instance, validated_data):
        members = validated_data.pop("members", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if members is not None:
            instance.members.set(set([instance.owner, *members]))
        return instance


class ExpenseSerializer(serializers.ModelSerializer):
    paid_by_details = UserSerializer(source="paid_by", read_only=True)
    participant_details = UserSerializer(source="participants", many=True, read_only=True)
    group_name = serializers.CharField(source="group.name", read_only=True)

    class Meta:
        model = Expense
        fields = (
            "id",
            "group",
            "group_name",
            "title",
            "description",
            "amount",
            "paid_by",
            "paid_by_details",
            "participants",
            "participant_details",
            "created_at",
        )
        read_only_fields = ("id", "group_name", "paid_by_details", "participant_details", "created_at")

    def validate_group(self, group):
        user = self.context["request"].user
        if not group.members.filter(id=user.id).exists():
            raise serializers.ValidationError("Voce nao participa deste grupo.")
        return group

    def validate(self, attrs):
        group = attrs.get("group") or getattr(self.instance, "group", None)
        paid_by = attrs.get("paid_by") or getattr(self.instance, "paid_by", None)
        participants = attrs.get("participants")

        if attrs.get("amount", getattr(self.instance, "amount", Decimal("0"))) <= 0:
            raise serializers.ValidationError({"amount": "O valor deve ser maior que zero."})

        if group and paid_by and not group.members.filter(id=paid_by.id).exists():
            raise serializers.ValidationError({"paid_by": "O pagador deve ser membro do grupo."})

        if participants is not None:
            if not participants:
                raise serializers.ValidationError({"participants": "Informe ao menos um participante."})
            member_ids = set(group.members.values_list("id", flat=True))
            invalid = [user.id for user in participants if user.id not in member_ids]
            if invalid:
                raise serializers.ValidationError(
                    {"participants": "Todos os participantes devem ser membros do grupo."}
                )
        return attrs
