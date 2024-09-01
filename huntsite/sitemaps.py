from django.contrib import sitemaps
from django.urls import reverse


class StaticViewSitemap(sitemaps.Sitemap):
    changefreq = "daily"
    protocol = "https"

    def priority(self, item):
        if item == "home":
            return 1.0
        return 0.5

    def items(self):
        return ["home", "about", "puzzle_list", "story", "team_list"]

    def location(self, item):
        return reverse(item)
