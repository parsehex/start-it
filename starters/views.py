from django.shortcuts import render
from .models import Starter
from django.utils import timezone
from datetime import timedelta
from django.db.models import Count


def admin_index_context(request):
	if not request.user.is_staff:
		return {}

	now = timezone.now()
	week_ago = now - timedelta(days=7)

	context = {
	    'total_starters': Starter.objects.count(),
	    'languages_count': Starter.objects.values('language').distinct().count(),
	    'recent_additions':
	    Starter.objects.filter(created_at__gte=week_ago).count(),
	    'latest_starters': Starter.objects.order_by('-created_at')[:5],
	}

	return context


def starter_list(request):
	starters = Starter.objects.all().order_by("-created_at")
	return render(request, "starters/list.html", {"starters": starters})


def landing_page(request):
	return render(request, "landing.html")
