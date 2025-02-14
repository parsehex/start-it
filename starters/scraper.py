from typing import Optional
import requests
from urllib.parse import urlparse
from datetime import datetime


class StarterScraper:

	def __init__(self, repo_url: str):
		self.repo_url = repo_url
		self.api_url = self._get_api_url()

	def _get_api_url(self) -> Optional[str]:
		"""Convert repository URL to API URL."""
		parsed = urlparse(self.repo_url)
		if 'github.com' in parsed.netloc:
			# Convert github.com/user/repo to api.github.com/repos/user/repo
			path = parsed.path.strip('/')
			return f'https://api.github.com/repos/{path}'
		return None

	def scrape(self) -> dict:
		"""Scrape repository information."""
		if not self.api_url:
			raise ValueError("Unsupported repository host")

		# print('scraping', self.api_url)
		response = requests.get(self.api_url)
		if response.status_code != 200:
			raise ValueError("Failed to fetch repository data")

		data = response.json()

		# Get language data
		languages_url = data.get('languages_url')
		languages = []
		if languages_url:
			lang_response = requests.get(languages_url)
			if lang_response.status_code == 200:
				languages = list(lang_response.json().keys())

		name = data.get('name')
		description = data.get('description')
		language = languages[0] if languages else None
		license = data.get('license', {})
		if license:
			license = license.get('spdx_id')
		updated_at = datetime.strptime(data.get('updated_at'),
		                               '%Y-%m-%dT%H:%M:%SZ')
		returnData = {
		    'name': name,
		    'description': description,
		    'language': language,
		    'license': license,
		    'updated_at': updated_at
		}
		return returnData
