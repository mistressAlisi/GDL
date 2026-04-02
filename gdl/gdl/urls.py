from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include, re_path
from django.views.generic import TemplateView

from cashier.api_views.bootstrap import gibootstrap_handler

urlpatterns = [
    path("grappelli/", include("grappelli.urls")),
    path("admin/", admin.site.urls),
    path("sln/",include("sportslottonet.urls")),
    path("slv/",include("sportslottonet.urls")),
    path("api/v1/bootstrap",gibootstrap_handler,name="gibootstrap_handler"),
    path("api/v1/", include("gdl.api_urls")),


    # SPA fallback — must be LAST
    re_path(
        r"^(?!api/|admin/|grappelli/).*$",
        TemplateView.as_view(template_name="frontend/index.html"),
    ),
]

if settings.USE_LOCAL_MEDIA:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += static(
        settings.STATIC_URL,
        document_root=settings.STATICFILES_DIRS[0],
    )