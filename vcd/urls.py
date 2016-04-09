from django.conf.urls import url

from vcd.views import loginview
from vcd.views import vmview

urlpatterns = [
    url(r'^$', vmview.orgsview),
    url(r'^login$', loginview.login_user),
    url(r'^logout$', loginview.logout_user),
    url(r'^(?P<org>[a-zA-Z]+)$', vmview.orgview),
]
