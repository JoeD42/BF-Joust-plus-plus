from django.contrib import admin

from .models import HillGame, HillProgram
# Register your models here.
admin.site.register(HillProgram)
admin.site.register(HillGame)