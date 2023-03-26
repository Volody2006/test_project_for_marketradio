from django.contrib import admin

from demo.models import (
    CompositionAudd,
    CompositionDiscogs,
    CompositionGenius,
    SearchName
)

# Register your models here.

admin.site.register(CompositionDiscogs)
admin.site.register(CompositionGenius)
admin.site.register(CompositionAudd)
admin.site.register(SearchName)
