from django.urls import path
from . import views
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('register/', views.register),
    path('login/', TokenObtainPairView.as_view()),
    path('refresh/', TokenRefreshView.as_view()),
    path('crops/', views.crop_list),
    path('simulate/', views.simulate),
    path('request-loan/', views.request_loan),
    path('api/interswitch/verify-customer/', views.verify_customer),
    path('api/interswitch/credit-score/', views.credit_score),
]