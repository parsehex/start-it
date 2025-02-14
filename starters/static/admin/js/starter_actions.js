function scrapeStarter(starterId) {
	if (!confirm('Are you sure you want to refresh this starter\'s information?')) {
		return;
	}

	// Get CSRF token from cookies
	const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;

	fetch('/admin/starters/starter/' + starterId + '/scrape/', {
		method: 'POST',
		headers: {
			'X-CSRFToken': csrftoken,
			'Content-Type': 'application/json',
		},
	})
		.then(response => response.json())
		.then(data => {
			if (data.success) {
				alert('Starter information updated successfully!');
				location.reload();
			} else {
				alert('Error updating starter: ' + data.error);
			}
		})
		.catch(error => {
			alert('Error: ' + error);
		});
}
