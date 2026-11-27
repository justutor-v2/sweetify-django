from django.core.serializers.json import DjangoJSONEncoder

# Django's encoder now handles lazy translations directly.
LazyEncoder = DjangoJSONEncoder
