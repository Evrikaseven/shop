from django.urls import path, include
from .zakazschik import urls as zakazschik_urls
from .zakupschik import urls as zakupschik_urls
from .sborschik import urls as sborschik_urls
from .administrator import urls as administrator_urls


urlpatterns = [
    path('zakazschik/', include(zakazschik_urls)),
    path('zakupschik/', include(zakupschik_urls)),
    path('sborschik/', include(sborschik_urls)),
    path('administrator/', include(administrator_urls)),
]
