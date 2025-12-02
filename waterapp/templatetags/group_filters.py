from django import template

register = template.Library()

@register.filter(name='has_group')
def has_group(user, group_name):
    """
    Usage in template: {% if request.user|has_group:"Technician" %}
    """
    return user.groups.filter(name=group_name).exists()