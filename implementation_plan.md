# Pawn Class — Refactoring Implementation Plan

Implementing 10 refactoring items from [pawn_refactoring.md](file:///c:/Users/admin/Documents/Kirk/Projects/queens-pawning/docs/pawn_refactoring.md) in priority order (skip #1 logging). Changes are confined to [pawn/models.py](file:///c:/Users/admin/Documents/Kirk/Projects/queens-pawning/pawn/models.py), [pawn/views.py](file:///c:/Users/admin/Documents/Kirk/Projects/queens-pawning/pawn/views.py), [access_hub/admin.py](file:///c:/Users/admin/Documents/Kirk/Projects/queens-pawning/access_hub/admin.py), [reports/views.py](file:///c:/Users/admin/Documents/Kirk/Projects/queens-pawning/reports/views.py), and the relevant HTML templates.

---

## Proposed Changes

### #3 — Fix [renewed_from](file:///c:/Users/admin/Documents/Kirk/Projects/queens-pawning/pawn/models.py#616-624) → `@property` (correctness bug)

#### [MODIFY] [models.py](file:///c:/Users/admin/Documents/Kirk/Projects/queens-pawning/pawn/models.py)
- Add `@property` decorator to [renewed_from](file:///c:/Users/admin/Documents/Kirk/Projects/queens-pawning/pawn/models.py#616-624).
- Fix [is_pawn_edittable](file:///c:/Users/admin/Documents/Kirk/Projects/queens-pawning/pawn/models.py#625-630) — the `self.renewed_from is None` check was comparing a bound method to `None` (always `False`), now it will correctly evaluate the property result.

#### [MODIFY] [views.py](file:///c:/Users/admin/Documents/Kirk/Projects/queens-pawning/pawn/views.py)
- Change `pawn.renewed_from()` (call) → `pawn.renewed_from` (property access). Currently on line 154.

---

### #4 — Unify [hasPenalty](file:///c:/Users/admin/Documents/Kirk/Projects/queens-pawning/pawn/models.py#336-339) to reuse [getElapseDays()](file:///c:/Users/admin/Documents/Kirk/Projects/queens-pawning/pawn/models.py#270-279)

#### [MODIFY] [models.py](file:///c:/Users/admin/Documents/Kirk/Projects/queens-pawning/pawn/models.py)
- Replace the inline elapsed-days calculation in [hasPenalty()](file:///c:/Users/admin/Documents/Kirk/Projects/queens-pawning/pawn/models.py#336-339) with `self.getElapseDays(date)`.

---

### #2 — Fix typo [is_pawn_edittable](file:///c:/Users/admin/Documents/Kirk/Projects/queens-pawning/pawn/models.py#625-630) → `is_pawn_editable`

#### [MODIFY] [models.py](file:///c:/Users/admin/Documents/Kirk/Projects/queens-pawning/pawn/models.py)
- Rename [is_pawn_edittable](file:///c:/Users/admin/Documents/Kirk/Projects/queens-pawning/pawn/models.py#625-630) → `is_pawn_editable`.

> No external call sites found for this method — only referenced in [models.py](file:///c:/Users/admin/Documents/Kirk/Projects/queens-pawning/pawn/models.py) itself.

---

### #6 — Extract `_upsert_cash_entry` shared helper

#### [MODIFY] [models.py](file:///c:/Users/admin/Documents/Kirk/Projects/queens-pawning/pawn/models.py)
- Add private `_upsert_cash_entry(model_class, cashier, description, amount, new_entry, ticket, payee_field)`.
- Refactor [update_receipts](file:///c:/Users/admin/Documents/Kirk/Projects/queens-pawning/pawn/models.py#505-544) and [update_disbursements](file:///c:/Users/admin/Documents/Kirk/Projects/queens-pawning/pawn/models.py#545-579) to delegate to this helper. Public signatures remain unchanged.

---

### #7 — Split [pay()](file:///c:/Users/admin/Documents/Kirk/Projects/queens-pawning/pawn/models.py#407-478) into [_redeem()](file:///c:/Users/admin/Documents/Kirk/Projects/queens-pawning/pawn/models.py#641-650) / [_renew()](file:///c:/Users/admin/Documents/Kirk/Projects/queens-pawning/pawn/models.py#499-504) helpers

#### [MODIFY] [models.py](file:///c:/Users/admin/Documents/Kirk/Projects/queens-pawning/pawn/models.py)
- Extract private `_build_renewed_pawn(...)` to encapsulate the new [Pawn](file:///c:/Users/admin/Documents/Kirk/Projects/queens-pawning/pawn/models.py#53-663) object construction.
- Extract private `_handle_redeem(cashier, amount_paid)` and `_handle_renew(post, cashier, amount_paid, ...)`.
- [pay()](file:///c:/Users/admin/Documents/Kirk/Projects/queens-pawning/pawn/models.py#407-478) becomes a thin dispatcher. Public signature of [pay()](file:///c:/Users/admin/Documents/Kirk/Projects/queens-pawning/pawn/models.py#407-478) is unchanged.

---

### #5 — Cache `get_instance()` calls

#### [MODIFY] [models.py](file:///c:/Users/admin/Documents/Kirk/Projects/queens-pawning/pawn/models.py)
- In [getPenalty](file:///c:/Users/admin/Documents/Kirk/Projects/queens-pawning/pawn/models.py#354-375): assign `OtherFees.get_instance()` to a local variable once; remove the redundant deferred-field guard (penalty_rate is always present in a normal query).
- In [getMinimumPayment](file:///c:/Users/admin/Documents/Kirk/Projects/queens-pawning/pawn/models.py#396-406): assign `OtherFees.get_instance()` to a local variable once.

---

### #9 — Rename [date](file:///c:/Users/admin/Documents/Kirk/Projects/queens-pawning/pawn/models.py#17-25) param → `as_of_date` in [getAdditionalInterest](file:///c:/Users/admin/Documents/Kirk/Projects/queens-pawning/pawn/models.py#308-320)

#### [MODIFY] [models.py](file:///c:/Users/admin/Documents/Kirk/Projects/queens-pawning/pawn/models.py)
- Rename parameter in definition and all internal usages.

#### [MODIFY] [views.py](file:///c:/Users/admin/Documents/Kirk/Projects/queens-pawning/pawn/views.py)
- Update call on line 223: `pawn.getAdditionalInterest(renew_redeem_date)` — positional arg, no change needed to the call itself, just confirms it still works.

---

### #8 — Remove [update_cash_position_new_ticket](file:///c:/Users/admin/Documents/Kirk/Projects/queens-pawning/pawn/models.py#580-582)

#### [MODIFY] [models.py](file:///c:/Users/admin/Documents/Kirk/Projects/queens-pawning/pawn/models.py)
- Remove the one-liner method [update_cash_position_new_ticket](file:///c:/Users/admin/Documents/Kirk/Projects/queens-pawning/pawn/models.py#580-582).
- Update its only internal caller (inside [pay()](file:///c:/Users/admin/Documents/Kirk/Projects/queens-pawning/pawn/models.py#407-478) after splitting) to call [update_cash_position_renew_ticket(cashier, description, self, new_entry)](file:///c:/Users/admin/Documents/Kirk/Projects/queens-pawning/pawn/models.py#583-609) directly.

---

### #11 — Consolidate [getInterestPlusPenalty](file:///c:/Users/admin/Documents/Kirk/Projects/queens-pawning/pawn/models.py#376-383) into [getMinTotalDue](file:///c:/Users/admin/Documents/Kirk/Projects/queens-pawning/pawn/models.py#390-392)

#### [MODIFY] [models.py](file:///c:/Users/admin/Documents/Kirk/Projects/queens-pawning/pawn/models.py)
- Verify they are identical: both return [getInterest() + getPenalty() + getAdditionalInterest()](file:///c:/Users/admin/Documents/Kirk/Projects/queens-pawning/pawn/models.py#299-307) → **yes, confirmed**.
- Remove [getInterestPlusPenalty](file:///c:/Users/admin/Documents/Kirk/Projects/queens-pawning/pawn/models.py#376-383) and keep [getMinTotalDue](file:///c:/Users/admin/Documents/Kirk/Projects/queens-pawning/pawn/models.py#390-392) (more descriptive).
- Add a deprecation alias `getInterestPlusPenalty = getMinTotalDue` so templates keep working without change, then update templates to use [getMinTotalDue](file:///c:/Users/admin/Documents/Kirk/Projects/queens-pawning/pawn/models.py#390-392).

#### [MODIFY] Templates using [getInterestPlusPenalty](file:///c:/Users/admin/Documents/Kirk/Projects/queens-pawning/pawn/models.py#376-383):
- `pawn/pawn_renew.html` line 55
- `pawn/pawn_redeem.html` line 51
- `pawn/pawn_detail_old.html` line 168

---

### #10 — Full snake_case rename

> [!IMPORTANT]
> This is done last. All renames add the snake_case method and keep the old camelCase name as a simple alias (`old_name = new_name`) to avoid dual maintenance. Then all templates and Python call sites are updated to the new name and the aliases can be removed later.

#### [MODIFY] [models.py](file:///c:/Users/admin/Documents/Kirk/Projects/queens-pawning/pawn/models.py)
Renames (old → new):

| Old | New |
|---|---|
| [getPTN](file:///c:/Users/admin/Documents/Kirk/Projects/queens-pawning/pawn/models.py#239-245) *(property)* | `ptn` |
| [getElapseDays](file:///c:/Users/admin/Documents/Kirk/Projects/queens-pawning/pawn/models.py#270-279) | `get_elapsed_days` |
| [getInterestRate](file:///c:/Users/admin/Documents/Kirk/Projects/queens-pawning/pawn/models.py#280-284) | `get_interest_rate` |
| [advanceInterestRate](file:///c:/Users/admin/Documents/Kirk/Projects/queens-pawning/pawn/models.py#285-295) *(static)* | `advance_interest_rate` |
| [getAdvanceInterestRate](file:///c:/Users/admin/Documents/Kirk/Projects/queens-pawning/pawn/models.py#296-298) | `get_advance_interest_rate` |
| [getInterest](file:///c:/Users/admin/Documents/Kirk/Projects/queens-pawning/pawn/models.py#299-307) | `get_interest` |
| [getAdditionalInterest](file:///c:/Users/admin/Documents/Kirk/Projects/queens-pawning/pawn/models.py#308-320) | `get_additional_interest` |
| [getAdvanceInterest](file:///c:/Users/admin/Documents/Kirk/Projects/queens-pawning/pawn/models.py#321-323) | `get_advance_interest` |
| [hasMatured](file:///c:/Users/admin/Documents/Kirk/Projects/queens-pawning/pawn/models.py#324-327) | `has_matured` |
| [get_maturity_date](file:///c:/Users/admin/Documents/Kirk/Projects/queens-pawning/pawn/models.py#328-330) | *(already snake_case)* |
| [hasExpired](file:///c:/Users/admin/Documents/Kirk/Projects/queens-pawning/pawn/models.py#331-335) | `has_expired` |
| [hasPenalty](file:///c:/Users/admin/Documents/Kirk/Projects/queens-pawning/pawn/models.py#336-339) | `has_penalty` |
| [getStanding](file:///c:/Users/admin/Documents/Kirk/Projects/queens-pawning/pawn/models.py#340-347) | `get_standing` |
| [getAuctionInterest](file:///c:/Users/admin/Documents/Kirk/Projects/queens-pawning/pawn/models.py#348-350) | `get_auction_interest` |
| [getPrincipalPlusAuctionInterest](file:///c:/Users/admin/Documents/Kirk/Projects/queens-pawning/pawn/models.py#351-353) | `get_principal_plus_auction_interest` |
| [getPenalty](file:///c:/Users/admin/Documents/Kirk/Projects/queens-pawning/pawn/models.py#354-375) | `get_penalty` |
| [getInterestPlusPenalty](file:///c:/Users/admin/Documents/Kirk/Projects/queens-pawning/pawn/models.py#376-383) | *(removed in #11)* |
| [getPrincipalPlusInterest](file:///c:/Users/admin/Documents/Kirk/Projects/queens-pawning/pawn/models.py#384-386) | `get_principal_plus_interest` |
| [getTotalDue](file:///c:/Users/admin/Documents/Kirk/Projects/queens-pawning/pawn/models.py#387-389) | `get_total_due` |
| [getMinTotalDue](file:///c:/Users/admin/Documents/Kirk/Projects/queens-pawning/pawn/models.py#390-392) | `get_min_total_due` |
| [getRenewalServiceFee](file:///c:/Users/admin/Documents/Kirk/Projects/queens-pawning/pawn/models.py#393-395) | `get_renewal_service_fee` |
| [getMinimumPayment](file:///c:/Users/admin/Documents/Kirk/Projects/queens-pawning/pawn/models.py#396-406) | `get_minimum_payment` |

#### [MODIFY] Templates (update all call sites):
- `pawn/pawn_detail.html`
- `pawn/pawn_renew.html`
- `pawn/pawn_redeem.html`
- `pawn/pawn_detail_old.html`
- `files/client_detail.html`
- [templates/dashboard.html](file:///c:/Users/admin/Documents/Kirk/Projects/queens-pawning/templates/dashboard.html)
- `reports/auction_overall.html`

#### [MODIFY] Python files (update all call sites):
- [pawn/views.py](file:///c:/Users/admin/Documents/Kirk/Projects/queens-pawning/pawn/views.py)
- [access_hub/admin.py](file:///c:/Users/admin/Documents/Kirk/Projects/queens-pawning/access_hub/admin.py)
- [reports/views.py](file:///c:/Users/admin/Documents/Kirk/Projects/queens-pawning/reports/views.py)

---

## Verification Plan

No automated tests exist for this model. Verification will be done by running the development server and exercising the key flows.

### Automated Check
```powershell
# Run from project root — confirms no import/syntax errors
python manage.py check
```

### Manual Smoke Tests (after each group of changes)
1. **Pawn detail page** — Navigate to an active pawn ticket. Confirm:
   - Pawn ticket number, elapsed days, interest rate, interest, additional interest, penalty row, total due, minimum payment all display correctly.
   - If the pawn was renewed from another ticket, the "Renewed from" link appears and links correctly.
2. **Renew flow** — Open a pawn ticket and click Renew. Confirm:
   - Interest + penalty field shows correct value.
   - Min total due field shows correct value.
   - Submitting the form creates a new ticket and marks the old one as RENEWED.
3. **Redeem flow** — Open a pawn ticket and click Redeem. Confirm:
   - Total due field shows correct value.
   - Submitting the form marks the ticket as REDEEMED.
4. **Dashboard** — Confirm pawn ticket numbers render on the dashboard table.
5. **Client detail** — Confirm pawn ticket links display correctly.
