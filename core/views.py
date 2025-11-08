from datetime import datetime, date
from calendar import monthrange
from decimal import Decimal
from django.db.models import Sum
from django.http import HttpResponse
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.views import APIView
from rest_framework.response import Response

from .models import Account, Category, Transaction, Goal, Budget
from .serializers import (
    AccountSerializer, CategorySerializer, TransactionSerializer, GoalSerializer, BudgetSerializer
)

class IsOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return getattr(obj, "user_id", None) == request.user.id

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

class BaseOwnedViewSet(viewsets.ModelViewSet):
    permission_classes = [IsOwner]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

class AccountViewSet(BaseOwnedViewSet):
    queryset = Account.objects.all()
    serializer_class = AccountSerializer

class CategoryViewSet(BaseOwnedViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

def _parse_date(s: str):
    try:
        return datetime.strptime(s, "%Y-%m-%d").date()
    except Exception:
        return None

class TransactionViewSet(BaseOwnedViewSet):
    queryset = Transaction.objects.all().order_by("-date","-id")
    serializer_class = TransactionSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        # filtros GET opcionais
        start = _parse_date(self.request.query_params.get("start_date", ""))
        end = _parse_date(self.request.query_params.get("end_date", ""))
        kind = self.request.query_params.get("kind")
        account_id = self.request.query_params.get("account_id")
        category_id = self.request.query_params.get("category_id")

        if start:
            qs = qs.filter(date__gte=start)
        if end:
            qs = qs.filter(date__lte=end)
        if kind in ("INCOME","EXPENSE","TRANSFER"):
            qs = qs.filter(kind=kind)
        if account_id:
            qs = qs.filter(account_id=account_id)
        if category_id:
            qs = qs.filter(category_id=category_id)
        return qs

    @action(detail=False, methods=["get"], url_path="export")
    def export_csv(self, request):
        # usa o mesmo queryset com os filtros acima
        qs = self.get_queryset().select_related("account","category")
        response = HttpResponse(content_type="text/csv; charset=utf-8")
        response["Content-Disposition"] = "attachment; filename=transactions.csv"
        # cabeçalho
        response.write("id,date,kind,amount,account,category,note\n")
        for t in qs:
            acct = (t.account.name if t.account_id else "")
            cat = (t.category.name if t.category_id else "")
            note = (t.note or "").replace('"','\"')
            line = f'{t.id},{t.date},{t.kind},{t.amount},{acct},{cat},"{note}"\n'
            response.write(line)
        return response

class GoalViewSet(BaseOwnedViewSet):
    queryset = Goal.objects.all()
    serializer_class = GoalSerializer

class BudgetViewSet(BaseOwnedViewSet):
    queryset = Budget.objects.all()
    serializer_class = BudgetSerializer

class DashboardView(APIView):
    permission_classes = [IsOwner]

    def get(self, request):
        user = request.user
        # período padrão: mês atual
        today = date.today()
        start = _parse_date(request.query_params.get("start_date", "")) or today.replace(day=1)
        end = _parse_date(request.query_params.get("end_date", "")) or today.replace(day=monthrange(today.year, today.month)[1])

        tx = Transaction.objects.filter(user=user, date__gte=start, date__lte=end)
        income = tx.filter(kind="INCOME").aggregate(total=Sum("amount"))["total"] or Decimal("0")
        expense = tx.filter(kind="EXPENSE").aggregate(total=Sum("amount"))["total"] or Decimal("0")
        balance = income - expense

        # despesas por categoria
        by_cat_qs = tx.filter(kind="EXPENSE").values("category__id","category__name").annotate(total=Sum("amount")).order_by("-total")
        by_category = [{"category_id": r["category__id"], "category": r["category__name"], "total": str(r["total"])} for r in by_cat_qs]

        # orçamentos do mês (ano/mês do 'start')
        budgets = Budget.objects.filter(user=user, year=start.year, month=start.month).select_related("category")
        budget_items = []
        for b in budgets:
            spent = tx.filter(kind="EXPENSE", category=b.category).aggregate(total=Sum("amount"))["total"] or Decimal("0")
            budget_items.append({
                "category": b.category.name,
                "planned": str(b.planned),
                "spent": str(spent),
                "remaining": str(max(Decimal("0"), b.planned - spent)),
                "status": "OK" if spent <= b.planned else "OVER",
            })

        # metas (saldo estimado da conta vinculada)
        goals = Goal.objects.filter(user=user).select_related("account")
        goals_items = []
        for g in goals:
            acct_tx = Transaction.objects.filter(user=user, account=g.account, date__lte=end)
            acct_income = acct_tx.filter(kind="INCOME").aggregate(total=Sum("amount"))["total"] or Decimal("0")
            acct_expense = acct_tx.filter(kind="EXPENSE").aggregate(total=Sum("amount"))["total"] or Decimal("0")
            acct_balance = acct_income - acct_expense
            progress = min(100, int((acct_balance / g.target_amount) * 100)) if g.target_amount else 0
            goals_items.append({
                "goal": g.name,
                "target_amount": str(g.target_amount),
                "due_date": g.due_date.isoformat() if g.due_date else None,
                "account": g.account.name if g.account_id else None,
                "estimated_balance": str(acct_balance),
                "progress_percent": progress,
            })

        data = {
            "period": {"start_date": start.isoformat(), "end_date": end.isoformat()},
            "totals": {"income": str(income), "expense": str(expense), "balance": str(balance)},
            "by_category_expense": by_category,
            "budgets": budget_items,
            "goals": goals_items,
        }
        return Response(data)
