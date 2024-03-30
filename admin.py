from django.contrib import admin
from .models import QueueEntry

# Register your models here.
class QueueEntryAdmin(admin.ModelAdmin):
    pass

admin.site.register(QueueEntry, QueueEntryAdmin)