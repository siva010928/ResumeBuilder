from django.conf import settings
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.routers import SimpleRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from app.users.api.views import UserViewSet

from app.resumes.views import ResumeViewSet

router = DefaultRouter() if settings.DEBUG else SimpleRouter()

router.register("users", UserViewSet, basename="users")
router.register("resumes", ResumeViewSet, basename="resumes")


app_name = "api"
urlpatterns = router.urls

urlpatterns += [
    path('login/', include("app.google_login_server_flow.urls", namespace='login')),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
