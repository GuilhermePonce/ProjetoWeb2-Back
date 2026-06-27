from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


DEMO_USERS = (
    {"username": "ana", "email": "ana@divideai.local", "first_name": "Ana"},
    {"username": "bruno", "email": "bruno@divideai.local", "first_name": "Bruno"},
    {"username": "carla", "email": "carla@divideai.local", "first_name": "Carla"},
)


class Command(BaseCommand):
    help = "Cria ou atualiza tres usuarios para testes locais."

    def add_arguments(self, parser):
        parser.add_argument(
            "--password",
            default="DivideAi123!",
            help="Senha definida para os tres usuarios.",
        )

    def handle(self, *args, **options):
        user_model = get_user_model()
        password = options["password"]

        for user_data in DEMO_USERS:
            user, created = user_model.objects.update_or_create(
                username=user_data["username"],
                defaults={
                    "email": user_data["email"],
                    "first_name": user_data["first_name"],
                },
            )
            user.set_password(password)
            user.save(update_fields=["password"])
            action = "criado" if created else "atualizado"
            self.stdout.write(
                self.style.SUCCESS(
                    f"{user.username} ({user.email}) - {action}"
                )
            )

        self.stdout.write(self.style.WARNING(f"Senha comum: {password}"))

