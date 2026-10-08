# from django.contrib import admin
# from .models import Sponsor


# @admin.register(Sponsor)
# class SponsorAdmin(admin.ModelAdmin):
#     list_display = ("name", "event")
#     search_fields = ("name",)


from django.contrib import admin
from .models import Sponsor

@admin.register(Sponsor)
class SponsorAdmin(admin.ModelAdmin):
    list_display  = ["name", "tier", "category", "active"]
    list_editable = ["active", "category"]
    list_filter   = ["tier", "category", "active"]
    search_fields = ["name", "tagline"]

    def get_changelist(self, request, **kwargs):
        BaseCL = super().get_changelist(request, **kwargs)
        if not request.user.is_authenticated or request.user.is_superuser:
            return BaseCL

        from django.db.models import Case, When, Value, IntegerField

        class ScopedSponsorChangeList(BaseCL):
            def get_queryset(self, request):
                qs = super().get_queryset(request)
                return qs.annotate(
                    _is_my=Case(
                        When(created_by=request.user, then=Value(0)),
                        default=Value(1),
                        output_field=IntegerField(),
                    )
                ).order_by("_is_my", *self.get_ordering(request, qs))

        return ScopedSponsorChangeList

    def get_changelist_form(self, request, **kwargs):
        FormClass = super().get_changelist_form(request, **kwargs)
        class ScopedSponsorChangelistForm(FormClass):
            def __init__(self, *f_args, **f_kwargs):
                super().__init__(*f_args, **f_kwargs)
                if not request.user.is_superuser:
                    # If this sponsor was not added by the current user, disable inline editing for active and category
                    if self.instance and self.instance.pk and self.instance.created_by_id != request.user.id:
                        if "active" in self.fields:
                            del self.fields["active"]
                        if "category" in self.fields:
                            del self.fields["category"]
        return ScopedSponsorChangelistForm

    def has_view_permission(self, request, obj=None):
        return True

    def has_change_permission(self, request, obj=None):
        if obj is None or request.user.is_superuser:
            return True
        return obj.created_by_id == request.user.id

    def has_delete_permission(self, request, obj=None):
        if obj is None or request.user.is_superuser:
            return True
        return obj.created_by_id == request.user.id

    def get_readonly_fields(self, request, obj=None):
        if not request.user.is_superuser and obj and obj.created_by_id != request.user.id:
            return [f.name for f in self.model._meta.fields]
        return super().get_readonly_fields(request, obj)

    def save_model(self, request, obj, form, change):
        if not change and not obj.created_by:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
