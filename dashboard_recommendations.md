# Dashboard Recommendations — Queens Pawning

## Current State

The dashboard already shows 4 stat boxes (all branch-aware):
| Variable | Meaning |
|---|---|
| `transactionsCountToday` | Pawn tickets granted today |
| `newClientCountToday` | New clients registered today |
| `maturedToday` | Active tickets past maturity date |
| `expiredToday` | Active tickets past expiration date |

It also renders a **Bulletin** card (from `bulletin_list` context — model not yet visible but template is ready).

---

## Recommended Additions

### 1 — KPI Stat Boxes (Row 1 — Quick Numbers)

Keep the four existing boxes and add:

| New Box | Data Source | Color |
|---|---|---|
| **Active Inventory Value** | `Pawn.inventory.aggregate(Sum('principal'))` | `bg-primary` |
| **Pending Discount Requests** | `DiscountRequests.objects.filter(status='PENDING')` | `bg-danger` |
| **Today's Expenses** | `Expense.objects.filter(date=today).aggregate(Sum('amount'))` | `bg-warning` |
| **Tickets On Hold** | `Pawn.objects.filter(on_hold=True, status='ACTIVE')` | `bg-dark` |

**Why:** Matured/expired counts tell you *risk*; these four add *financial exposure* and *operations pulse*.

---

### 2 — Alerts / Action Required Panel

A red/orange callout card listing items needing immediate attention:

- **Expired tickets not on hold** (i.e., `Pawn.expired.filter(on_hold=False)`) — links to the Non-Renewal / Auction Report
- **Pending discount requests** — links to the Discount Requests list

> [!IMPORTANT]
> This is the highest-value addition. Staff currently have to navigate away to find these. Surfacing them on the dashboard prevents missed auctions.

---

### 3 — Financial Summary Card (Today's Cash Position Snapshot)

Show a mini summary for the user's branch for **today**:

| Item | Source |
|---|---|
| Balance COH | `DailyCashPosition.balance_coh` |
| Total Receipts | `DailyCashPosition.get_total_receipts()` |
| Total Disbursements | `DailyCashPosition.get_total_disbursements()` |
| **Net Total** | `DailyCashPosition.get_net_total()` |

This saves branch staff from navigating to the full Daily Cash Position report just to see the running total.

---

### 4 — Transaction Trend Chart (Last 7 Days)

A simple bar or line chart (Chart.js) showing **new pawn tickets per day** for the past 7 days. Query:

```python
from django.db.models.functions import TruncDate
from django.db.models import Count

Pawn.objects.filter(
    date_granted__gte=today - timedelta(days=6)
).annotate(day=TruncDate('date_granted'))
 .values('day')
 .annotate(count=Count('id'))
 .order_by('day')
```

Pass as JSON to the template for `Chart.js`.

**Why:** Spot seasonal patterns and slow days without opening a report.

---

### 5 — Item Type Breakdown (Doughnut Chart)

A doughnut chart of active inventory grouped by `item_description`:

```python
Pawn.inventory.values('item_description').annotate(count=Count('id'))
```

Useful for quickly knowing which item types dominate the current portfolio.

---

### 6 — Recent Transactions Table

A compact table of the **10 most recent pawn tickets** (any status), quick-linking to each detail page. Columns: PTN, Client, Principal, Status, Date Granted.

```python
Pawn.objects.order_by('-date_encoded')[:10]
```

---

## Implementation Checklist

| Task | File |
|---|---|
| Add new context variables | [access_hub/views.py](file:///c:/Users/admin/Documents/Kirk/Projects/queens-pawning/access_hub/views.py) → [dashboard()](file:///c:/Users/admin/Documents/Kirk/Projects/queens-pawning/access_hub/views.py#11-34) |
| Add `bulletin_list` if not yet wired | [access_hub/views.py](file:///c:/Users/admin/Documents/Kirk/Projects/queens-pawning/access_hub/views.py) (needs a `Bulletin` model or similar) |
| Add Chart.js CDN or local static | [templates/base.html](file:///c:/Users/admin/Documents/Kirk/Projects/queens-pawning/templates/base.html) or [templates/dashboard.html](file:///c:/Users/admin/Documents/Kirk/Projects/queens-pawning/templates/dashboard.html) |
| New template sections | [templates/dashboard.html](file:///c:/Users/admin/Documents/Kirk/Projects/queens-pawning/templates/dashboard.html) |

### Context variables to add in [dashboard()](file:///c:/Users/admin/Documents/Kirk/Projects/queens-pawning/access_hub/views.py#11-34):

```python
from django.db.models import Sum, Count
from expense.models import Expense
from pawn.models import Pawn, DiscountRequests
from reports.models import DailyCashPosition

# Existing
today = date.today()
employee = Employee.objects.get(user=request.user)
branch = employee.branch

# New
active_portfolio_value = Pawn.inventory.filter(**branch_filter).aggregate(Sum('principal'))['principal__sum'] or 0
pending_discounts     = DiscountRequests.objects.filter(status='PENDING', **branch_pawn_filter).count()
expenses_today        = Expense.objects.filter(date=today, **branch_filter).aggregate(Sum('amount'))['amount__sum'] or 0
on_hold_count         = Pawn.objects.filter(on_hold=True, status='ACTIVE', **branch_filter).count()
expired_not_on_hold   = Pawn.expired.filter(on_hold=False, **branch_filter)
cash_position_today   = DailyCashPosition.objects.filter(branch=branch, date=today).first()

# 7-day chart data (serialize to JSON for Chart.js)
trend = list(
    Pawn.objects.filter(date_granted__gte=today - timedelta(6), **branch_filter)
        .annotate(day=TruncDate('date_granted'))
        .values('day').annotate(count=Count('id')).order_by('day')
)
```

---

## Priority Order

1. **Alerts panel** (expired-not-on-hold + pending discounts) — highest operational value
2. **Cash position snapshot** — replaces a daily navigation trip
3. **Two new stat boxes** (portfolio value + on-hold count)
4. **7-day trend chart** — nice-to-have visual
5. **Item type doughnut** — nice-to-have visual
6. **Recent transactions table** — convenience
