from django.contrib import admin, messages
from django.contrib.admin import AdminSite
from django.contrib.auth.admin import UserAdmin, GroupAdmin
from django.contrib.auth.models import User, Group
from django.utils.html import format_html
from .models import Starter


class StartItAdminSite(AdminSite):
	site_header = 'Start It Administration'
	site_title = 'Start It Admin Portal'
	index_title = 'Site Management'


admin_site = StartItAdminSite(name='startit_admin')
admin_site.register(User, UserAdmin)
admin_site.register(Group, GroupAdmin)


@admin.register(Starter)
class StarterAdmin(admin.ModelAdmin):
	list_display = ("name", "display_repo_link", "language", "stack", "license",
	                "created_at")
	list_filter = ("language", "license", "created_at")
	search_fields = ("name", "description", "language", "stack", "license")
	readonly_fields = ("created_at", "updated_at")
	fieldsets = (
	    ("Basic Information", {
	        "fields": ("name", "description", "repo_url"),
	    }),
	    ("Technical Details", {
	        "fields": ("language", "stack", "license"),
	        "classes": ("collapse", ),
	    }),
	    ("Metadata", {
	        "fields": ("created_at", "updated_at"),
	        "classes": ("collapse", ),
	    }),
	)

	actions = ['scrape_repository']

	def get_queryset(self, request):
		qs = super().get_queryset(request)
		return qs.order_by('-created_at')

	def display_repo_link(self, obj):
		return format_html('<a href="{}" target="_blank">{}</a>', obj.repo_url,
		                   obj.repo_url)

	display_repo_link.short_description = "Repository URL"

	class Media:
		css = {'all': ['admin/css/custom_admin.css']}

	def display_repo_link(self, obj):
		return format_html('<a href="{}" target="_blank">{}</a>', obj.repo_url,
		                   obj.repo_url)

	def scrape_repository(self, request, queryset):
		"""Admin action to scrape repository information."""
		success_count = 0
		for starter in queryset:
			if starter.update_from_repo():
				success_count += 1

		if success_count:
			message = f'Successfully updated {success_count} starter(s)'
			self.message_user(request, message, messages.SUCCESS)
		else:
			self.message_user(request, "Failed to update starters", messages.ERROR)

	scrape_repository.short_description = "Scrape repository information"
	display_repo_link.short_description = "Repository URL"

	def save_model(self, request, obj, form, change):
		# Auto-capitalize language names
		if obj.language:
			obj.language = obj.language.capitalize()
		super().save_model(request, obj, form, change)


admin_site.register(Starter, StarterAdmin)
