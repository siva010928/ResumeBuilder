from django.urls import path

from app.google_login_server_flow.apis import (
    GoogleLoginApi,
    GoogleLoginRedirectApi,
)

app_name = "login"
urlpatterns = [
    path("callback/", GoogleLoginApi.as_view(), name="callback"),
    path("redirect/", GoogleLoginRedirectApi.as_view(), name="redirect"),
]
