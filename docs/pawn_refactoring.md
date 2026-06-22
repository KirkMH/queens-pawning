# Pawn Class — Refactoring Recommendations

Each item below is self-contained so you can pick and implement any combination.
Items are grouped by theme and rated by **impact** (benefit gained) and **risk** (chance of introducing a regression).

---

## 1. Replace `print()` with `logging`

**Impact:** Medium | **Risk:** Very Low

All debugging `print()` calls throughout the class should be replaced with proper Python `logging` calls. This allows log levels to be controlled at runtime and removes noise from production.

**Affected methods:** `getAdditionalInterest`, `advanceInterestRate`, `getPenalty`, `getInterestPlusPenalty`, `update_payment`, `update_receipts`, `update_disbursements`, `update_cash_position_renew_ticket`, `update_renew_redeem_date`, `renewed_from`, `is_deleteable`, `reset_status`, `hasExpired`.

```python
# Before
print(f"Elapsed: {elapsed}")

# After
import logging
logger = logging.getLogger(__name__)
logger.debug("Elapsed: %s", elapsed)
```

---

## 2. Fix Typo: `is_pawn_edittable` → `is_pawn_editable`

**Impact:** Low | **Risk:** Low (requires updating all call sites)

The method name has a double `t`. Fix the spelling and update all references in views and templates.

```python
# Before
def is_pawn_edittable(self):

# After
def is_pawn_editable(self):
```

> **Note:** Search for `is_pawn_edittable` across views, templates, and serializers before renaming.

---

## 3. Convert `renewed_from()` to a `@property`

**Impact:** Low | **Risk:** Very Low

`renewed_from` is used as if it were a field (e.g. `self.renewed_from is None` in `is_pawn_edittable`), but it is defined as a regular method. This is a bug — the check `self.renewed_from is None` will **never** be `True` because a bound method is never `None`. Converting it to a `@property` fixes the logic.

```python
# Before
def renewed_from(self):
    ...

# After
@property
def renewed_from(self):
    ...
```

> ⚠️ **This is a correctness fix, not just style.** The `is_pawn_edittable` check `self.renewed_from is None` currently always evaluates to `False`, meaning no ticket is ever considered editable by that check.

---

## 4. Unify `hasPenalty()` to Reuse `getElapseDays()`

**Impact:** Medium | **Risk:** Low

`hasPenalty(date)` independently recomputes elapsed days instead of calling `getElapseDays(date)`. This creates two different elapsed-day calculations that can drift out of sync.

```python
# Before
def hasPenalty(self, date=None):
    elapsed = ((date if date else to_date(self.renew_redeem_date)) - to_date(self.date_granted)).days
    return elapsed > TermDuration.get_instance().maturity

# After
def hasPenalty(self, date=None):
    return self.getElapseDays(date) > TermDuration.get_instance().maturity
```

---

## 5. Cache `TermDuration.get_instance()` and `OtherFees.get_instance()`

**Impact:** Medium | **Risk:** Very Low

`TermDuration.get_instance()` and `OtherFees.get_instance()` are called multiple times within a single request (e.g. inside `getPenalty`, `hasMatured`, `hasExpired`, `hasPenalty`, `getMinimumPayment`). Each call hits the database. Cache the result in a local variable when used more than once in a method, or use a module-level cached property.

```python
# Before
def getPenalty(self, date=None):
    if self.hasPenalty(date):
        ...
        other_fees = OtherFees.get_instance()
        deferred_fields = other_fees.get_deferred_fields()
        if 'penalty_rate' in deferred_fields:
            other_fees.refresh_from_db(fields=['penalty_rate'])
        penalty_rate = other_fees.penalty_rate

# After — the deferred-fields guard can be removed if penalty_rate
# is always selected; or extract a helper:
def _get_penalty_rate(self):
    return OtherFees.get_instance().penalty_rate
```

---

## 6. Extract Shared Logic from `update_receipts` and `update_disbursements`

**Impact:** High | **Risk:** Medium

These two methods are nearly identical — they both:
1. Resolve the ticket and date,
2. Get-or-create a `DailyCashPosition`,
3. Delete existing entries for the ticket,
4. Get-or-create a new entry,
5. Populate and save the entry.

The only differences are the model (`AddReceipts` vs `LessDisbursements`) and the field names (`received_from` vs `payee`). Extract a private helper:

```python
def _upsert_cash_entry(self, model_class, cashier, description, amount,
                        new_entry, ticket, payee_field):
    ticket = ticket or self
    date = ticket.date_granted
    if description == "Redeemed" and self.renew_redeem_date:
        date = self.renew_redeem_date

    cash_position, _ = DailyCashPosition.objects.get_or_create(
        branch=ticket.branch, date=date
    )
    model_class.objects.filter(pawn=ticket).delete()
    entry, _ = model_class.objects.get_or_create(
        daily_cash_position=cash_position, pawn=ticket
    )
    if new_entry:
        cash_position.prepared_by = cashier
        cash_position.save()

    entry.reference_number = ticket.getPTN
    setattr(entry, payee_field, ticket.client.full_name)
    entry.particulars = description
    entry.amount = amount
    entry.automated = True
    entry.save()
    return entry


def update_receipts(self, cashier, description, amount, new_entry=True, ticket=None):
    return self._upsert_cash_entry(
        AddReceipts, cashier, description, amount, new_entry, ticket, 'received_from'
    )


def update_disbursements(self, cashier, description, amount, new_entry=True, ticket=None):
    return self._upsert_cash_entry(
        LessDisbursements, cashier, description, amount, new_entry, ticket, 'payee'
    )
```

---

## 7. Split `pay()` into `_redeem()` and `_renew()` Helpers

**Impact:** High | **Risk:** Medium

`pay()` handles both redemption and renewal in a single method with branching logic, making it long and hard to follow. Splitting the branches into private helpers improves readability and testability.

```python
def pay(self, post, cashier):
    amount_paid = Decimal(post.get('amtToPay'))
    if amount_paid >= self.principal:
        self._redeem(post, cashier, amount_paid)
    else:
        self._renew(post, cashier, amount_paid)

def _redeem(self, post, cashier, amount_paid):
    # redemption logic only
    ...

def _renew(self, post, cashier, amount_paid):
    # renewal + new pawn creation logic only
    ...
```

---

## 8. Remove `update_cash_position_new_ticket` or Clarify Its Purpose

**Impact:** Low | **Risk:** Very Low

`update_cash_position_new_ticket` is a one-liner that calls `update_cash_position_renew_ticket(cashier, description, self, new_entry)`. It adds a layer of indirection without meaningful distinction. Either:
- **Remove it** and call `update_cash_position_renew_ticket` directly with `self` as the ticket, or
- **Document it** clearly to explain why the two entry points are needed.

---

## 9. Clarify `getAdditionalInterest(date=None)` Parameter Name

**Impact:** Low | **Risk:** Very Low

The parameter `date` shadows Python's built-in `date` type (which is imported at the top of the file). Rename it to `as_of_date` or `renewal_date` for clarity.

```python
# Before
def getAdditionalInterest(self, date=None):

# After
def getAdditionalInterest(self, as_of_date=None):
```

---

## 10. Standardise Method Naming to `snake_case`

**Impact:** Medium | **Risk:** Medium (many call sites)

Python and Django convention is `snake_case` for methods. The class currently mixes camelCase (`getInterest`, `getPenalty`, `getElapseDays`, etc.) with snake_case (`has_matured` would be conventional). 

**Recommendation:** Rename all `get*`/`has*`/`is*` methods to snake_case and add deprecation aliases if needed to avoid breaking views and templates in one go.

| Current | Recommended |
|---|---|
| `getElapseDays` | `get_elapsed_days` |
| `getInterestRate` | `get_interest_rate` |
| `getInterest` | `get_interest` |
| `getAdditionalInterest` | `get_additional_interest` |
| `getAdvanceInterest` | `get_advance_interest` |
| `getAdvanceInterestRate` | `get_advance_interest_rate` |
| `hasMatured` | `has_matured` |
| `hasExpired` | `has_expired` |
| `hasPenalty` | `has_penalty` |
| `getStanding` | `get_standing` |
| `getPenalty` | `get_penalty` |
| `getInterestPlusPenalty` | `get_interest_plus_penalty` |
| `getAuctionInterest` | `get_auction_interest` |
| `getPrincipalPlusAuctionInterest` | `get_principal_plus_auction_interest` |
| `getPrincipalPlusInterest` | `get_principal_plus_interest` |
| `getTotalDue` | `get_total_due` |
| `getMinTotalDue` | `get_min_total_due` |
| `getRenewalServiceFee` | `get_renewal_service_fee` |
| `getMinimumPayment` | `get_minimum_payment` |
| `getPTN` *(property)* | `ptn` |

> **Note:** This is a large-scale rename. Do it last, after all other refactorings are done, and use a project-wide search to update all call sites.

---

## 11. Clarify `getInterestPlusPenalty` Name

**Impact:** Low | **Risk:** Very Low

`getInterestPlusPenalty()` actually returns `interest + penalty + additional_interest` — the name omits `additional_interest`. Rename to `get_interest_penalty_and_additional` or simply consolidate with `getMinTotalDue()` since they produce the same result.

> Check: `getInterestPlusPenalty()` = `getMinTotalDue()`. If they are identical, one can be removed.

---

## Priority Order (Suggested)

| # | Item | Why first |
|---|---|---|
| 1 | **#3 — Fix `renewed_from` property bug** | Correctness fix; currently broken |
| 2 | **#4 — Unify `hasPenalty` with `getElapseDays`** | Correctness / consistency |
| 3 | **#1 — Replace `print()` with `logging`** | Low risk, immediate production benefit |
| 4 | **#2 — Fix `is_pawn_edittable` typo** | Low risk |
| 5 | **#6 — Extract `_upsert_cash_entry`** | High impact, removes duplication |
| 6 | **#7 — Split `pay()` into helpers** | High impact, improves testability |
| 7 | **#5 — Cache `get_instance()` calls** | Medium impact, easy to do |
| 8 | **#9 — Rename `date` param** | Trivial |
| 9 | **#8 — Clean up `update_cash_position_new_ticket`** | Minor cleanup |
| 10 | **#11 — Clarify `getInterestPlusPenalty`** | Minor naming |
| 11 | **#10 — Full snake_case rename** | Large scope, do last |
