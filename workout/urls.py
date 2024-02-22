from rest_framework import routers

from workout import views

router = routers.DefaultRouter()

router.register(r'workout', views.WorkoutViewSet)
router.register(r'workout-component', views.WorkoutComponentViewSet)

urlpatterns = []
urlpatterns += router.urls
