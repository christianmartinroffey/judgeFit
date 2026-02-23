from rest_framework import routers

from athlete import views

router = routers.DefaultRouter()

router.register(r'athletes', views.AthleteViewSet)
router.register(r'competitions', views.CompetitionViewSet)

urlpatterns = []

urlpatterns += router.urls
