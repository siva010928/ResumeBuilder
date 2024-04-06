from django.urls import path

from app.google_login_server_flow.apis import (
    GoogleLoginApi,
    GoogleLoginRedirectApi, CustomLoginApi,
)

app_name = "login"
urlpatterns = [
    path("callback/", GoogleLoginApi.as_view(), name="callback"),
    path("redirect/", GoogleLoginRedirectApi.as_view(), name="redirect"),
    path("get-tokens/", CustomLoginApi.as_view(), name="get_tokens"),
]
