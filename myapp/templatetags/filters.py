import requests
from django import template
from django.conf import settings
from myapp.models import UserPreferences
from decimal import Decimal, InvalidOperation

register = template.Library()

CURRENCY_SYMBOLS = {
    "USD": "$",
    "INR": "₹",
    "EUR": "€",
    "GBP": "£",
}

CONVERSION_RATES = {}

def get_conversion_rate(from_currency, to_currency):
    global CONVERSION_RATES

    if (from_currency, to_currency) in CONVERSION_RATES:
        return CONVERSION_RATES[(from_currency, to_currency)]
    
    API_KEY = "CBJDZKLW9MNVED5J"
    url = f"https://www.alphavantage.co/query?function=CURRENCY_EXCHANGE_RATE&from_currency={from_currency}&to_currency={to_currency}&apikey={API_KEY}"

    response = requests.get(url)
    data = response.json()

    try:
        rate = Decimal(data["Realtime Currency Exchange Rate"]["5. Exchange Rate"])
        CONVERSION_RATES[(from_currency, to_currency)] = rate
        return rate
    except (KeyError, InvalidOperation):
        return Decimal('1.00')  # Default to 1 if API fails or conversion error

@register.filter
def currency_format(amount, user):
    user_pref, _ = UserPreferences.objects.get_or_create(user=user)
    selected_currency = user_pref.currency  

    base_currency = "INR"
    try:
        amount = Decimal(amount)  # Ensure amount is Decimal
        if selected_currency != base_currency:
            conversion_rate = get_conversion_rate(base_currency, selected_currency)
            amount *= conversion_rate  # Safe multiplication with Decimal
    except (InvalidOperation, TypeError):
        pass  # In case of any error, keep the original amount

    symbol = CURRENCY_SYMBOLS.get(selected_currency, "₹")
    return f"{symbol}{amount:.2f}"

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key, None)