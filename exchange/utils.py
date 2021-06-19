from django.conf import settings

from authentication.utils import random_text


def validate_exchange_amount(amount, value):
    '''
    amount is the amount of <currency> for the exchange deal,
    value is the amount of the <currency> for a dollar(<currency>/USD)
    '''
    # calc_amt is in dollars
    calc_amt = amount / value
    if (calc_amt) < settings.EXCHANGE_MINIMUM:
        # convert exchange minimum from dollar to fund currency
        min_in_fund_currency = settings.EXCHANGE_MINIMUM * value
        return (False, min_in_fund_currency,)
    return (True, 0,)

def get_usable_uid(instance, uid=None):
	if not uid:
		uid = random_text(10)

    # Check if the uid exists in the model table
	exists = instance.__class__.objects.filter(uid=uid).exists()
	if exists:
		return get_usable_uid(instance, random_text(10))
	return uid