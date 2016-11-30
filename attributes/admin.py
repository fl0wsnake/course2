from django.contrib import admin
from attributes.models import *

admin.site.register(AttributeType)
admin.site.register(Attribute)
admin.site.register(Suffix)
admin.site.register(Option)
admin.site.register(OptionValue)
admin.site.register(IntValue)
admin.site.register(FloatValue)
admin.site.register(VarcharValue)
