from django.urls import path
from workstream.views.workstream_views import WorkStreamCreateView

urlpatterns = [
    path("workstreams/", WorkStreamCreateView.as_view(), name="workstream-create"),
]

