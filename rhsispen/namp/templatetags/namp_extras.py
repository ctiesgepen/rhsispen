from django import template
from datetime import timedelta as TimeDelta

register = template.Library()

@register.filter(name='add_month')
def add_month(value):
    return value + TimeDelta(days=30)

@register.filter(name='less_month')
def less_month(value):
    return value + TimeDelta(days=-30)


#@register.inclusion_tag(name='date_hierarchy')
 #   def date_hierarchy(value):        
   #     return value + ()