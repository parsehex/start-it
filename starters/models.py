from django.db import models


class Starter(models.Model):
	name = models.CharField(max_length=255)
	description = models.TextField(blank=True, null=True)
	repo_url = models.URLField()
	language = models.CharField(max_length=100, blank=True, null=True)
	stack = models.CharField(max_length=255, blank=True, null=True)
	license = models.CharField(max_length=100, blank=True, null=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	def __str__(self):
		return self.name

	def update_from_repo(self):
		"""Update starter information from repository."""
		from .scraper import StarterScraper
		try:
			scraper = StarterScraper(self.repo_url)
			data = scraper.scrape()

			# Update fields
			self.name = data.get('name', self.name)
			self.description = data.get('description', self.description)
			self.language = data.get('language', self.language)
			self.license = data.get('license', self.license)
			self.save()
			return True
		except Exception as e:
			return False
