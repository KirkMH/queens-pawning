import os
import re

directories = [
    r'c:\Users\admin\Documents\Kirk\Projects\queens-pawning\templates\pawn',
    r'c:\Users\admin\Documents\Kirk\Projects\queens-pawning\templates\reports',
    r'c:\Users\admin\Documents\Kirk\Projects\queens-pawning\templates\files',
    r'c:\Users\admin\Documents\Kirk\Projects\queens-pawning\templates',
    r'c:\Users\admin\Documents\Kirk\Projects\queens-pawning\pawn',
    r'c:\Users\admin\Documents\Kirk\Projects\queens-pawning\reports',
    r'c:\Users\admin\Documents\Kirk\Projects\queens-pawning\access_hub'
]

replacements = [
    (r'\bgetPTN\b', 'ptn'),
    (r'\brenewed_from\(\)', 'renewed_from'),
    (r'\bgetElapseDays\b', 'get_elapsed_days'),
    (r'\bgetInterestRate\b', 'get_interest_rate'),
    (r'\badvanceInterestRate\b', 'advance_interest_rate'),
    (r'\bgetAdvanceInterestRate\b', 'get_advance_interest_rate'),
    (r'\bgetInterest\b', 'get_interest'),
    (r'\bgetAdditionalInterest\b', 'get_additional_interest'),
    (r'\bgetAdvanceInterest\b', 'get_advance_interest'),
    (r'\bhasMatured\b', 'has_matured'),
    (r'\bhasExpired\b', 'has_expired'),
    (r'\bhasPenalty\b', 'has_penalty'),
    (r'\bgetStanding\b', 'get_standing'),
    (r'\bgetAuctionInterest\b', 'get_auction_interest'),
    (r'\bgetPrincipalPlusAuctionInterest\b', 'get_principal_plus_auction_interest'),
    (r'\bgetPenalty\b', 'get_penalty'),
    (r'\bgetPrincipalPlusInterest\b', 'get_principal_plus_interest'),
    (r'\bgetTotalDue\b', 'get_total_due'),
    (r'\bgetMinTotalDue\b', 'get_min_total_due'),
    (r'\bgetRenewalServiceFee\b', 'get_renewal_service_fee'),
    (r'\bgetMinimumPayment\b', 'get_minimum_payment'),
    (r'\bgetInterestPlusPenalty\b', 'get_min_total_due'), # Special replacement for item 11
]

for dir_path in directories:
    if not os.path.exists(dir_path): continue
    for root, dirs, files in os.walk(dir_path):
        for f_name in files:
            if f_name.endswith('.html') or f_name.endswith('.py'):
                f_path = os.path.join(root, f_name)
                # Skip models.py because we already did it and don't want to mess up the aliases
                if f_name == 'models.py' and 'pawn' in root:
                    continue
                with open(f_path, 'r', encoding='utf-8') as f:
                    try:
                        content = f.read()
                    except UnicodeDecodeError:
                        continue
                
                original_content = content
                for old, new in replacements:
                    content = re.sub(old, new, content)
                
                if content != original_content:
                    with open(f_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    print(f"Updated {f_path}")

print("Call sites renamed successfully")
