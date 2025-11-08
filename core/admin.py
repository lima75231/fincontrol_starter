from django.contrib import admin
from .models import Account, Category, Transaction, Goal, Budget, RecurringRule

@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ("id","name","kind","user","opening_balance")

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id","name","type","user","parent")

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ("id","kind","amount","date","user","account","category","is_recurring")
    list_filter = ("kind","is_recurring","date")

@admin.register(Goal)
class GoalAdmin(admin.ModelAdmin):
    list_display = ("id","name","target_amount","due_date","user","account")

@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    list_display = ("id","category","year","month","planned","user")

@admin.register(RecurringRule)
class RecurringRuleAdmin(admin.ModelAdmin):
    list_display = ("id","user","frequency","day","next_run","transaction_template")
