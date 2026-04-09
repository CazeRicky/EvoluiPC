from django.contrib import admin

from .models import MachineSnapshot


# Configura listagem no admin Django.
@admin.register(MachineSnapshot)
class MachineSnapshotAdmin(admin.ModelAdmin):
    list_display = ("user", "source", "collected_at")
    search_fields = ("user__username", "source")
