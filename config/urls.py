from django.urls import path, include
from rest_framework.routers import DefaultRouter
from clients.views import ClientViewSet
from ingestion.views import IngestionJobViewSet
from records.views import NormalizedRecordViewSet, RawRecordViewSet

router = DefaultRouter()
router.register(r'clients', ClientViewSet, basename='client')
router.register(r'ingestion/jobs', IngestionJobViewSet, basename='job')
router.register(r'records', NormalizedRecordViewSet, basename='record')
router.register(r'raw_records', RawRecordViewSet, basename='raw_record')

urlpatterns = [
    path('api/', include(router.urls)),
]
