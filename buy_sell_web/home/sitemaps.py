from django.contrib import sitemaps
from django.urls import reverse
from django.contrib.sites.models import Site

class StaticViewSitemap(sitemaps.Sitemap):
    priority = 0.8
    changefreq = 'daily'

    def get_urls(self, site=None, **kwargs):
        site = Site(domain='www.exontime.com', name='www.exontime.com')
        return super(StaticViewSitemap, self).get_urls(site=site, **kwargs)

    def items(self):
        return ['home', 'about_us', 'login', 'register', 'terms_conditions', 'priv_poli', 'aml_poli', 'refund_poli', 'help']

    def location(self, item):
        return reverse(item)
