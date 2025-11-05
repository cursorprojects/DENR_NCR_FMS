from django import template
from decimal import Decimal

register = template.Library()

@register.filter
def currency(value):
    """
    Format a number as Philippine peso currency with commas and 2 decimal places.
    """
    if value is None or value == '':
        return '₱0.00'
    
    try:
        # Convert to Decimal for precise decimal handling
        if isinstance(value, str):
            value = Decimal(value)
        elif isinstance(value, (int, float)):
            value = Decimal(str(value))
        
        # Format with commas and 2 decimal places
        formatted = f"{value:,.2f}"
        return f"₱{formatted}"
    except (ValueError, TypeError):
        return '₱0.00'

@register.filter
def currency_no_symbol(value):
    """
    Format a number with commas and 2 decimal places without the peso sign.
    """
    if value is None or value == '':
        return '0.00'
    
    try:
        # Convert to Decimal for precise decimal handling
        if isinstance(value, str):
            value = Decimal(value)
        elif isinstance(value, (int, float)):
            value = Decimal(str(value))
        
        # Format with commas and 2 decimal places
        return f"{value:,.2f}"
    except (ValueError, TypeError):
        return '0.00'