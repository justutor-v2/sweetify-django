import json

from django import template
from django.conf import settings
from django.template.loader import render_to_string

register = template.Library()


@register.simple_tag(takes_context=True)
def sweetify(context, nonce=None):
    payload = context.request.session.pop("sweetify", None)
    if not payload:
        return ""

    legacy = getattr(settings, "SWEETIFY_SWEETALERT_LIBRARY", "sweetalert2") == "sweetalert"
    if isinstance(payload, list) and legacy:
        raise RuntimeError("multiple alerts are currently not supported in sweetalert")

    messages = payload if isinstance(payload, list) else [payload]
    return render_to_string(
        "sweetify/alerts.html",
        {"alerts": [json.loads(message) for message in messages], "legacy": legacy, "nonce": nonce},
    )
