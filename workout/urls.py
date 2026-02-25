from rest_framework import routers

from workout import views

router = routers.DefaultRouter()

router.register(r'workouts', views.WorkoutsViewSet)
router.register(r'workout-components', views.WorkoutComponentsViewSet)
router.register(r'videos', views.VideosViewSet)

urlpatterns = []
urlpatterns += router.urls
