from django.conf import settings
from django.db import models

class Account(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=80)
    kind = models.CharField(max_length=20, choices=[("wallet","Wallet"),("bank","Bank"),("card","Card")])
    opening_balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.name} ({self.user})"

class Category(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=80)
    type = models.CharField(max_length=10, choices=[("INCOME","INCOME"),("EXPENSE","EXPENSE")])
    parent = models.ForeignKey("self", null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return self.name

class Transaction(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, null=True, blank=True, on_delete=models.SET_NULL)
    kind = models.CharField(max_length=10, choices=[("INCOME","INCOME"),("EXPENSE","EXPENSE"),("TRANSFER","TRANSFER")])
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    date = models.DateField()
    note = models.CharField(max_length=200, blank=True)
    is_recurring = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.kind} {self.amount} em {self.date}"

class RecurringRule(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    transaction_template = models.ForeignKey(Transaction, on_delete=models.CASCADE, related_name="recurring_rule")
    frequency = models.CharField(max_length=15, choices=[("WEEKLY","WEEKLY"),("MONTHLY","MONTHLY")])
    day = models.PositiveSmallIntegerField()  # ex.: dia do mês
    next_run = models.DateField()

class Goal(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=80)
    target_amount = models.DecimalField(max_digits=12, decimal_places=2)
    due_date = models.DateField(null=True, blank=True)
    account = models.ForeignKey(Account, null=True, blank=True, on_delete=models.SET_NULL)

class Budget(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    year = models.IntegerField()
    month = models.IntegerField()
    planned = models.DecimalField(max_digits=12, decimal_places=2)
