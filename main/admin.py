from django.contrib import admin
from .models import *

admin.site.register(Profile)
admin.site.register(MoneyBlock)
admin.site.register(Transaction)