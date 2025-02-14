from django import forms
from django.contrib import admin, messages
from django.contrib.admin import AdminSite
from django.contrib.auth.admin import UserAdmin, GroupAdmin
from django.contrib.auth.models import User, Group
from django.utils.html import format_html
from django.shortcuts import render, redirect
from django.urls import path

from starters.views import admin_index_context
from .models import Starter
from .scraper import StarterScraper


class StartItAdminSite(AdminSite):
	site_header = 'Start It Administration'
	site_title = 'Start It Admin Portal'
	index_title = 'Site Management'

	def get_urls(self):
		urls = super().get_urls()
		custom_urls = [
		    path('scrape-starter/',
		         self.admin_view(self.add_scrape_view),
		         name='scrape_starter'),
		]
		return custom_urls + urls

	def index(self, request, extra_context=None):
		extra_context = admin_index_context(request)
		extra_context['scrape_form'] = StarterScrapeForm()

		return super().index(request, extra_context)

	def add_scrape_view(self, request):
		"""Custom admin view to scrape and add a starter from a given URL."""
		if request.method == "POST":
			form = StarterScrapeForm(request.POST)
			if form.is_valid():
				repo_url = form.cleaned_data["repo_url"]
				scraper = StarterScraper(repo_url)
				try:
					data = scraper.scrape()
					starter, created = Starter.objects.update_or_create(
					    repo_url=repo_url,
					    defaults={
					        "name": data.get("name", "Unnamed Starter"),
					        "description": data.get("description", ""),
					        "language": data.get("language", ""),
					        "license": data.get("license", ""),
					    })

					if created:
						messages.success(request, "Starter added successfully!")
					else:
						messages.info(request, "Starter updated successfully!")

					return redirect(f"../starters/starter/{starter.id}/change/")
				except Exception as e:
					messages.error(request, f"Error: {e}")
		else:
			form = StarterScrapeForm()
		return render(request, "admin/scrape_starter.html", {"form": form})


admin_site = StartItAdminSite(name='startit_admin')
admin_site.register(User, UserAdmin)
admin_site.register(Group, GroupAdmin)


class StarterScrapeForm(forms.Form):
	repo_url = forms.URLField(label="Repository URL", required=True)


@admin.register(Starter)
class StarterAdmin(admin.ModelAdmin):
	list_display = ("name", "display_repo_link", "language", "stack", "license",
	                "created_at", "action_buttons")
	list_filter = ("language", "license", "created_at")
	search_fields = ("name", "description", "language", "stack", "license")
	readonly_fields = ("created_at", "updated_at")
	fieldsets = (
	    ("Basic Information", {
	        "fields": ("name", "description", "repo_url")
	    }),
	    ("Technical Details", {
	        "fields": ("language", "stack", "license"),
	        "classes": ("collapse", )
	    }),
	    ("Metadata", {
	        "fields": ("created_at", "updated_at"),
	        "classes": ("collapse", )
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

	def action_buttons(self, obj):
		"""Generate action buttons for each starter."""
		return format_html(
		    '<a class="button" href="{}" target="_blank">View Repo</a>'
		    '<button class="button" onclick="scrapeStarter({})" type="button">Refresh</button>',
		    obj.repo_url, obj.id)

	action_buttons.short_description = "Actions"

	class Media:
		css = {'all': ['admin/css/custom_admin.css']}
		js = ['admin/js/starter_actions.js']

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

	def save_model(self, request, obj, form, change):
		# Auto-capitalize language names
		if obj.language:
			obj.language = obj.language.capitalize()
		super().save_model(request, obj, form, change)


admin_site.register(Starter, StarterAdmin)
