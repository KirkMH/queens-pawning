# `Pawn` Model — Function Reference

**File:** `pawn/models.py`

The `Pawn` model represents a pawn transaction. Transactions are either **Accrued Interest (`ACC`)** or **Advance Interest (`ADV`)**, which affects how interest, penalties, and due amounts are computed.

---

## Properties

### `getPTN` → `str`
Returns the pawn ticket number (PTN) display string.
- If `pawn_ticket_number` is set, returns `"<PTN> (<transaction_type>)"`.
- Otherwise auto-generates one as `"<transaction_type>-<id:06d>"`.

---

### `complete_description` → `str`
Builds a human-readable description of the pawned item, combining quantity, carat, color, item type, additional description, and weight in grams.

---

### `expiration_date` → `date`
Returns the date on which the pawn ticket expires, calculated as:
```
date_granted + TermDuration.expiration (days)
```

---

### `transaction_type_label` → `str`
Returns the human-readable display label for the transaction type (e.g. `"Accrued Interest"` or `"Advance Interest"`).

---

## Interest & Rate Methods

### `getElapseDays(rrd=None)` → `int`
Returns the number of elapsed days used for interest calculation.
- For **ADV** transactions: days since `promised_renewal_date`.
- For **ACC** transactions: days since `date_granted`.
- `rrd` (renew/redeem date) defaults to today if not provided.

---

### `getInterestRate()` → `Decimal | 0`
Looks up the applicable accrued interest rate (from `InterestRate`) based on elapsed days. Returns `0` if no rate is found.

---

### `advanceInterestRate(promise_date, date_granted=None)` *(static)* → `Decimal | 0`
Looks up the advance interest rate (from `AdvanceInterestRate`) based on the number of days between `date_granted` and `promise_date`. Returns `0` if no rate found.

---

### `getAdvanceInterestRate()` → `Decimal | 0`
Instance-level wrapper for `advanceInterestRate()` using the pawn's own `promised_renewal_date` and `date_granted`.

---

### `getInterest()` → `Decimal`
Calculates the accrued interest:
```
principal × (interest_rate / 100)
```
Returns `0` for **ADV** transactions (interest is paid in advance).

---

### `getAdditionalInterest(date=None)` → `Decimal`
For **ADV** transactions, calculates the extra interest owed if the ticket is renewed past the promised date:
```
additional_interest = computed_interest - advance_interest  (if positive)
```
Returns `0` for **ACC** transactions.

---

### `getAdvanceInterest()` → `Decimal`
Calculates the advance interest amount:
```
principal × (advance_interest_rate / 100)
```

---

## Status & Standing Methods

### `hasMatured()` → `bool`
Returns `True` if the number of days since `date_granted` has reached or exceeded `TermDuration.maturity`.

---

### `get_maturity_date()` → `date`
Returns the maturity date:
```
date_granted + TermDuration.maturity (days)
```

---

### `hasExpired()` → `bool`
Returns `True` if the number of days since `date_granted` exceeds `TermDuration.expiration`.

---

### `hasPenalty(date=None)` → `bool`
Returns `True` if the elapsed days (from `date_granted` to `renew_redeem_date` or the given `date`) exceed `TermDuration.maturity`.

---

### `getStanding()` → `str`
Returns the effective standing of an active ticket:
- `'EXPIRED'` if `hasExpired()` is True
- `'MATURED'` if `hasMatured()` is True
- Otherwise, returns the current `status` value.

---

## Amount Calculation Methods

### `getPenalty(date=None)` → `Decimal | 0`
Calculates the penalty amount if `hasPenalty()` is True:
```
penalty = principal × (penalty_rate / 100) × (days_past_maturity / 30)
```
Returns `0` if no penalty applies.

---

### `getInterestPlusPenalty()` → `Decimal`
Returns the sum of accrued interest, penalty, and additional interest:
```
getInterest() + getPenalty() + getAdditionalInterest()
```

---

### `getAuctionInterest()` → `Decimal`
Returns the fixed auction interest:
```
principal × (4 × 0.04)   →   16% of principal
```

---

### `getPrincipalPlusAuctionInterest()` → `Decimal`
Returns `principal + getAuctionInterest()`.

---

### `getPrincipalPlusInterest()` → `Decimal`
Returns `principal + getInterest()`.

---

### `getTotalDue()` → `Decimal`
Returns the full redemption amount:
```
principal + interest + penalty + additional_interest
```

---

### `getMinTotalDue()` → `Decimal`
Returns the minimum amount due (without principal):
```
interest + penalty + additional_interest
```

---

### `getRenewalServiceFee()` → `Decimal`
Returns the service fee from `OtherFees`.

---

### `getMinimumPayment()` → `Decimal`
Returns the minimum payment required to renew a ticket:
```
interest (ACC only) + penalty + service_fee + additional_interest
```

---

## Transaction Methods

### `pay(post, cashier)`
Processes a payment (renewal or redemption) from POST data.
- If `amount_paid >= principal` → marks ticket as **REDEEMED**.
- Otherwise → creates a new `Pawn` ticket and marks the current one as **RENEWED**.
- Calls `update_payment()` and updates the daily cash position accordingly.

| Parameter | Description |
|-----------|-------------|
| `post` | Django `QueryDict` from the POST request |
| `cashier` | `Employee` instance performing the transaction |

---

### `update_payment(cashier, service_fee, advance_interest, amount_paid, paid_interest, penalty, paid_for_principal, discount_granted)`
Creates or updates the linked `Payment` record with the breakdown of a transaction.

---

### `update_receipts(cashier, description, amount, new_entry=True, ticket=None)` → `AddReceipts`
Creates or updates an `AddReceipts` entry in the `DailyCashPosition` for the given ticket. Deletes any pre-existing receipt for the same ticket before re-creating it.

---

### `update_disbursements(cashier, description, amount, new_entry=True, ticket=None)` → `LessDisbursements`
Creates or updates a `LessDisbursements` entry in the `DailyCashPosition` for the given ticket. Deletes any pre-existing disbursement record before re-creating it.

---

### `update_cash_position_new_ticket(cashier, description, new_entry=True)`
Convenience wrapper for `update_cash_position_renew_ticket()` using `self` as the new ticket.

---

### `update_cash_position_renew_ticket(cashier, description, new_ticket, new_entry=True)` → `(AddReceipts, LessDisbursements)`
Updates both the receipt and disbursement entries for a renewal or new ticket transaction.
- Receipt amount: `principal + interest + penalty` (if renewing), or `interest` only (if new).
- Disbursement amount: `new_ticket.principal - new_ticket.service_charge`.

---

### `auction()`
Marks the pawn ticket as **AUCTIONED** and records the timestamp.

---

### `reset_status()`
Resets the pawn ticket back to **ACTIVE**, clearing `renewed_to` and `renew_redeem_date`.

---

## Date & Lifecycle Helpers

### `update_renew_redeem_date(date=None)`
Sets `renew_redeem_date` to today (or the provided `date`) if the ticket is **ACTIVE** and the date has changed. Saves the record.

---

### `is_pawned_today()` → `bool`
Returns `True` if `date_granted` is today.

---

### `is_encoded_today()` → `bool`
Returns `True` if `date_encoded` is today.

---

### `get_last_renewal_date()` → `date | None`
Returns `date_granted` if this ticket has been renewed onward (`pawn_renewed_to` exists), otherwise `None`.

---

### `renewed_from()` → `Pawn | None`
Returns the **parent** pawn ticket that was renewed into this one, or `None` if this is an original ticket.

---

## Permission / Editability Methods

> These methods rely on `self.current_user` being set externally via `pawn.current_user = request.user`.

### `is_pawn_edittable()` → `bool`
Returns `True` if the ticket can be edited:
- Has no parent (not renewed from another ticket), **and**
- Status is `ACTIVE`, **and**
- The user is a head-office employee (no branch) **or** the ticket was encoded today.

---

### `is_voidable()` → `bool`
Returns `True` if the ticket can be voided (status is `REDEEMED` or `AUCTIONED`) and the user is a head-office employee.

---

### `is_deleteable()` → `bool`
Returns `True` if the ticket can be deleted (status is `ACTIVE`) and the user is a head-office employee.

---

## `__str__`

Returns: `"<PTN>: <client> - <complete_description>"`
