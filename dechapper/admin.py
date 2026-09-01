from django.contrib import admin

from .models import SiteConfiguration


@admin.register(SiteConfiguration)
class SiteConfigurationAdmin(admin.ModelAdmin):
    list_display = ("next_available",)

    def has_add_permission(self, request):
        return not SiteConfiguration.objects.exists()

