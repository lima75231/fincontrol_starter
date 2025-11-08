from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AccountViewSet, CategoryViewSet, TransactionViewSet, GoalViewSet, BudgetViewSet, DashboardView

router = DefaultRouter()
router.register(r'accounts', AccountViewSet)
router.register(r'categories', CategoryViewSet)
router.register(r'transactions', TransactionViewSet, basename="transactions")
router.register(r'goals', GoalViewSet)
router.register(r'budgets', BudgetViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
]
