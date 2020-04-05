from django.conf.urls import url, include
from rest_framework import routers
from rest_framework.routers import DefaultRouter
from .app.viewsets import HumanViewSet, LoginViewSet, CheckFaceViewSet

router = DefaultRouter()
router.register(r'human', HumanViewSet)
router.register(r'login', LoginViewSet)
router.register(r'check-face', CheckFaceViewSet)

urlpatterns = [
    url(r'^', include(router.urls)),

]
