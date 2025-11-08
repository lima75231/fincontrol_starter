from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from core.models import Category, Account

class Command(BaseCommand):
    help = "Cria categorias básicas e uma conta exemplo para o usuário admin."

    def handle(self, *args, **options):
        User = get_user_model()
        user = User.objects.first()
        if not user:
            self.stdout.write(self.style.WARNING("Crie um usuário primeiro (createsuperuser)."))
            return

        income = ["Salário","Freelance","Investimentos"]
        expense = ["Alimentação","Transporte","Moradia","Saúde","Educação","Lazer","Contas Fixas"]

        for name in income:
            Category.objects.get_or_create(user=user, name=name, type="INCOME")
        for name in expense:
            Category.objects.get_or_create(user=user, name=name, type="EXPENSE")

        Account.objects.get_or_create(user=user, name="Carteira", kind="wallet", defaults={"opening_balance":0})
        self.stdout.write(self.style.SUCCESS("Categorias e conta criadas com sucesso!"))
