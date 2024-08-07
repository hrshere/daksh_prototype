from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CategoryViewSet, ShapeViewSet, MaterialViewSet, RatingViewSet, ProductViewSet, ProductImageViewSet, CartViewSet,OrderViewSet

router = DefaultRouter()
router.register(r'categories', CategoryViewSet)
router.register(r'shapes', ShapeViewSet)
router.register(r'materials', MaterialViewSet)
router.register(r'ratings', RatingViewSet)
router.register(r'products', ProductViewSet)
router.register(r'product-images', ProductImageViewSet)
router.register(r'orders', OrderViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('cart/', CartViewSet.as_view({'get': 'list', 'post': 'create'})),
    path('cart/<int:pk>/update-quantity/', CartViewSet.as_view({'put': 'update_quantity'})),
    path('cart/<int:pk>/remove-item/', CartViewSet.as_view({'delete': 'remove_item'})),
    # path('orders/', OrderCreateView.as_view(), name='order-create'),  # Endpoint for creating orders

]
