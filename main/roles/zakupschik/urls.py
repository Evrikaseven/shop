from django.urls import path
import main.roles.zakupschik.views as views


urlpatterns = [
    path('main/', views.ZakupschikMainView.as_view(), name=views.ZakupschikMainView.url_name),
    path('individual_orders/', views.ZakupschikIndividualOrdersView.as_view(),
         name=views.ZakupschikIndividualOrdersView.url_name),
    path('joint_orders/', views.ZakupschikJointOrdersView.as_view(),
         name=views.ZakupschikJointOrdersView.url_name),
]