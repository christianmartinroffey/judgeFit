from rest_framework import routers

from athlete import views

router = routers.DefaultRouter()

router.register(r'athlete', views.AthleteViewSet)
router.register(r'competition', views.AthleteViewSet)

urlpatterns = []
urlpatterns += router.urls
