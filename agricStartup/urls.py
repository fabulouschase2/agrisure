from django.urls import path
from . import views
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('register/', views.register),
    path('login/', TokenObtainPairView.as_view()),
    path('refresh/', TokenRefreshView.as_view()),
    path('crops/', views.crop_list),
    path('simulate/', views.simulate),
    path('request-loan/', views.request_loan),

    # Interswitch Data
    path('interswitch/verify-customer/', views.verify_customer),
    path('interswitch/credit-score/', views.credit_score),
    path('interswitch/financial-history/', views.financial_history),
    path('interswitch/financial-habits/', views.financial_habits),

    # Interswitch Lending
    path('interswitch/loan-offers/', views.loan_offers),
    path('interswitch/accept-loan/', views.accept_loan),
    path('interswitch/verify-account/', views.verify_account),
    path('interswitch/update-loan-status/', views.update_loan_status),
]