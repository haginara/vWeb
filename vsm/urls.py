from django.conf.urls import url

from vsm.views import loginview
from vsm.views import edgeview

urlpatterns = [
    # Assets
    url(r'^$', edgeview.edgeview),
    #url(r'^login$', LoginView.as_view(), name='login'),
    url(r'^login$', loginview.login_vsm_user),
    url(r'^logout$', loginview.logout_vsm_user),
    url(r'^(?P<edgeId>edge-[0-9]+)$', edgeview.detailview),
]
