from django.urls import path
from django.conf import settings

from demo.views import (
    CompositionCreateView,
    CompositionDetailView,
    CompositionIndexView,
)

app_name = "demo"
urlpatterns = [
    path("", CompositionIndexView.as_view(), name="index"),
    path("search/", CompositionCreateView.as_view(), name="create"),
    path("<int:pk>/", CompositionDetailView.as_view(), name="detail"),
]

if settings.DEBUG:
    from django.conf.urls.static import static

    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL,
                          document_root=settings.STATIC_ROOT)
