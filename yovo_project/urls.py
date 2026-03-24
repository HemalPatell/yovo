from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

admin.site.site_header  = "🛍 YOVO Admin"
admin.site.site_title   = "YOVO Admin Portal"
admin.site.index_title  = "Marketplace Management"

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',       include('marketplace.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 = 'marketplace.views.handler404'
handler500 = 'marketplace.views.handler500'
