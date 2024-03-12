from django.conf import settings
from rest_framework.routers import DefaultRouter
from rest_framework.routers import SimpleRouter

from app.users.api.views import UserViewSet

from app.resumes.views import ResumeViewSet

router = DefaultRouter() if settings.DEBUG else SimpleRouter()

router.register("users", UserViewSet, basename="users")
router.register("resumes", ResumeViewSet, basename="resumes")


app_name = "api"
urlpatterns = router.urls
