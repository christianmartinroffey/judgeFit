from django.contrib import admin

from athlete.models import Country, Affiliate


# Register your models here.
class CountryAdmin(admin.ModelAdmin):
    list_display = ('name', 'router_code', 'code')
    list_filter = ('name', 'router_code', 'code')
    search_fields = ('name', 'router_code', 'code')


admin.site.register(Country, CountryAdmin)


class AffiliateAdmin(admin.ModelAdmin):
    list_display = ('name', 'city', 'country', 'crossfit_affiliate', 'created_at')
    list_filter = ('name', 'city', 'crossfit_affiliate', 'country', 'state')
    search_fields = ('name', 'city', 'country', 'state')


admin.site.register(Affiliate, AffiliateAdmin)
