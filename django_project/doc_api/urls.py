from django.urls import path, include
from rest_framework import routers
from . import views

router = routers.DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'groups', views.GroupViewSet)
router.register(r'sentiment', views.SentimentsView)

urlpatterns = [
    path('doc_api', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework'))
    
   
]