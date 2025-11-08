# fincontrol (Django monólito — MVP)

App de controle financeiro com Entradas, Saídas, Despesas Fixas/Variáveis, Metas e Orçamentos.
Pronto para rodar localmente com SQLite e exposto via API REST (DRF).

## Como rodar (dev)
```bash
python -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py createsuperuser
python manage.py seed_basic   # categorias e uma conta de exemplo
python manage.py runserver
```
Acesse: http://127.0.0.1:8000/api/ (browsable API) e /admin/ (admin)

## Endpoints principais
- /api/accounts/
- /api/categories/
- /api/transactions/
- /api/goals/
- /api/budgets/

Filtragem por usuário já configurada. Ao criar recursos na API, o `user` é definido automaticamente.

## Produção (resumo)
- Use PostgreSQL (set DB_URL no .env).
- Configure ALLOWED_HOSTS e DEBUG=False.
- Suba em Render/Railway/Fly (WSGI).
