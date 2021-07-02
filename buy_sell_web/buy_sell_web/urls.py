"""buy_sell_web URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls import url
from django.contrib import admin
from django.views.decorators.cache import cache_page
from home import views as views
from home.sitemaps import StaticViewSitemap
from django.contrib.sitemaps.views import sitemap
from django.urls import path

handler404 = views.error_404
#handler500 = views.error_404

sitemaps = {
    'static': StaticViewSitemap,
}

urlpatterns = [
    path('admin362880/', admin.site.urls),
    path('', include('home.urls')),
    url(r'^robots\.txt', include('robots.urls')),
    url(r'^google7b7a092bf0942f76\.html', views.google_ver, name='google_verification'),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='my-sitemap')
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)