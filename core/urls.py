from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from .views import *

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('create/', CreateProducts.as_view(), name='create'),
    path('list/', ListProducts.as_view(), name='list'),
    path('edit/<slug>/', EditProduct.as_view(), name='edit'),
    path('detail/<slug>/', ProductDetail.as_view(), name='detail'),
    path('create-checkout-session/<slug>/', CreateCheckoutSessionView.as_view(), name='create-checkout-session'),
    path('success/', SuccessView.as_view(), name='success'),
    path('webhooks/stripe/', stripe_webhook, name='webhooks-stripe'),
    path("library/<username>/", UserLibraryList.as_view(), name="library"),
    # path('test/', TestView.as_view(), name='test'),
    path('accounts/', include('allauth.urls')),
    path('admin/', admin.site.urls),
    path('marketplace/', include(('marketplace.urls', 'marketplace'))),
    path('users/', include(('accounts.urls', 'users'))),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)