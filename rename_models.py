import re

file_path = r'c:\Users\admin\Documents\Kirk\Projects\queens-pawning\pawn\models.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

replacements = [
    ('def getPTN(self):', 'def ptn(self):'),
    ('self.getPTN', 'self.ptn'),
    ('def getElapseDays(', 'def get_elapsed_days('),
    ('self.getElapseDays(', 'self.get_elapsed_days('),
    ('def getInterestRate(', 'def get_interest_rate('),
    ('self.getInterestRate(', 'self.get_interest_rate('),
    ('def advanceInterestRate(', 'def advance_interest_rate('),
    ('Pawn.advanceInterestRate(', 'Pawn.advance_interest_rate('),
    ('def getAdvanceInterestRate(', 'def get_advance_interest_rate('),
    ('self.getAdvanceInterestRate(', 'self.get_advance_interest_rate('),
    ('def getInterest(', 'def get_interest('),
    ('self.getInterest(', 'self.get_interest('),
    ('def getAdditionalInterest(', 'def get_additional_interest('),
    ('self.getAdditionalInterest(', 'self.get_additional_interest('),
    ('def getAdvanceInterest(', 'def get_advance_interest('),
    ('self.getAdvanceInterest(', 'self.get_advance_interest('),
    ('def hasMatured(', 'def has_matured('),
    ('self.hasMatured(', 'self.has_matured('),
    ('def hasExpired(', 'def has_expired('),
    ('self.hasExpired(', 'self.has_expired('),
    ('def hasPenalty(', 'def has_penalty('),
    ('self.hasPenalty(', 'self.has_penalty('),
    ('def getStanding(', 'def get_standing('),
    ('self.getStanding(', 'self.get_standing('),
    ('def getAuctionInterest(', 'def get_auction_interest('),
    ('self.getAuctionInterest(', 'self.get_auction_interest('),
    ('def getPrincipalPlusAuctionInterest(', 'def get_principal_plus_auction_interest('),
    ('self.getPrincipalPlusAuctionInterest(', 'self.get_principal_plus_auction_interest('),
    ('def getPenalty(', 'def get_penalty('),
    ('self.getPenalty(', 'self.get_penalty('),
    ('def getPrincipalPlusInterest(', 'def get_principal_plus_interest('),
    ('self.getPrincipalPlusInterest(', 'self.get_principal_plus_interest('),
    ('def getTotalDue(', 'def get_total_due('),
    ('self.getTotalDue(', 'self.get_total_due('),
    ('def getMinTotalDue(', 'def get_min_total_due('),
    ('self.getMinTotalDue(', 'self.get_min_total_due('),
    ('def getRenewalServiceFee(', 'def get_renewal_service_fee('),
    ('self.getRenewalServiceFee(', 'self.get_renewal_service_fee('),
    ('def getMinimumPayment(', 'def get_minimum_payment('),
    ('self.getMinimumPayment(', 'self.get_minimum_payment('),
]

for old, new in replacements:
    content = content.replace(old, new)
    
aliases = '''
    getPTN = property(ptn)
    getElapseDays = get_elapsed_days
    getInterestRate = get_interest_rate
    advanceInterestRate = advance_interest_rate
    getAdvanceInterestRate = get_advance_interest_rate
    getInterest = get_interest
    getAdditionalInterest = get_additional_interest
    getAdvanceInterest = get_advance_interest
    hasMatured = has_matured
    hasExpired = has_expired
    hasPenalty = has_penalty
    getStanding = get_standing
    getAuctionInterest = get_auction_interest
    getPrincipalPlusAuctionInterest = get_principal_plus_auction_interest
    getPenalty = get_penalty
    getPrincipalPlusInterest = get_principal_plus_interest
    getTotalDue = get_total_due
    getMinTotalDue = get_min_total_due
    getRenewalServiceFee = get_renewal_service_fee
    getMinimumPayment = get_minimum_payment
'''

# insert aliases right before the end of Pawn class, let's say before class Payment(models.Model):
content = content.replace('class Payment(models.Model):', aliases + '\nclass Payment(models.Model):')

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Models renamed successfully")
