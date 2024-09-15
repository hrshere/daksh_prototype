from rest_framework import viewsets, filters, status
from firebase_admin import messaging, credentials
import firebase_admin
import stripe
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from django.contrib.auth.models import User
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Category, Shape, Material, Rating, Product, ProductImage,Cart,CartItem
from .serializers import CategorySerializer, ShapeSerializer, MaterialSerializer, RatingSerializer, ProductSerializer, ProductImageSerializer,CartItemSerializer,CartSerializer,OrderSerializer,Order

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class ShapeViewSet(viewsets.ModelViewSet):
    queryset = Shape.objects.all()
    serializer_class = ShapeSerializer

class MaterialViewSet(viewsets.ModelViewSet):
    queryset = Material.objects.all()
    serializer_class = MaterialSerializer

class RatingViewSet(viewsets.ModelViewSet):
    queryset = Rating.objects.all()
    serializer_class = RatingSerializer

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter,DjangoFilterBackend]
    filterset_fields = ['material__id','category__id','shape__id','rating__id']
    search_fields = ['name']  # Adjust based on your model fields

    def get_queryset(self):
        queryset = Product.objects.all()
        ids = self.request.query_params.get('ids', None)
        if ids:
            try:
                id_list = [int(id) for id in ids.split(',') if id]
                queryset = queryset.filter(id__in=id_list)
            except ValueError:
                # Handle the case where IDs cannot be converted to integers
                queryset = Product.objects.none()  # or raise an exception if you prefer
        return queryset


    @action(detail=True, methods=['post'])
    def upload_images(self, request, pk=None):
        product = self.get_object()
        images = request.FILES.getlist('images')
        for image in images:
            ProductImage.objects.create(product=product, image=image)
        return Response(status=status.HTTP_201_CREATED)
    

class ProductImageViewSet(viewsets.ModelViewSet):
    queryset = ProductImage.objects.all()
    serializer_class = ProductImageSerializer

class CartViewSet(viewsets.ViewSet):
    def list(self, request):
        cart, created = Cart.objects.get_or_create(user=request.user)
        serializer = CartSerializer(cart)
        return Response(serializer.data)

    def create(self, request):
        product_id = request.data.get('product_id')
        quantity = request.data.get('quantity', 1)
        product = Product.objects.get(id=product_id)
        
        cart, created = Cart.objects.get_or_create(user=request.user)
        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
        
        if not created:
            cart_item.quantity += quantity
        else:
            cart_item.quantity = quantity
        cart_item.save()
        
        return Response(CartItemSerializer(cart_item).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['put'])
    def update_quantity(self, request, pk=None):
        cart_item = CartItem.objects.get(id=pk, cart__user=request.user)
        cart_item.quantity = request.data.get('quantity', cart_item.quantity)
        cart_item.save()
        return Response(CartItemSerializer(cart_item).data)

    @action(detail=True, methods=['delete'])
    def remove_item(self, request, pk=None):
        cart_item = CartItem.objects.get(id=pk, cart__user=request.user)
        cart_item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

stripe.api_key = "sk_test_51Pvco22NLuRsyXo47F1Q60xsGL5YVf1LaIDvFOYm1FflbaPPamWAg43LPIZwcOXIpgEdnlDmp5g40Kb1AxCMrubz00VptJSWBL"

@api_view(['POST'])
def create_payment_intent(request):
    try:
        data = request.data
        amount = data.get('amount')#cents
        intent = stripe.PaymentIntent.create(
            amount=amount,
            currency='usd'
        )
        return Response({'client_secret' : intent['client_secret']}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['POST'])
def send_push_notification(request):
    if not firebase_admin._apps:
        cred = credentials.Certificate("C:/Users/DELL/Downloads/daksh-ptype-firebase-adminsdk-4kdvg-c62907c850.json")
        firebase_admin.initialize_app(cred)

    try:
        data = request.data
        registration_token = data.get('token')
        # This registration token comes from the client FCM SDKs.
        # messaging = firebase_admin.initialize_app()
        # registration_token = 'YOUR_REGISTRATION_TOKEN'
        print(registration_token)

# See documentation on defining a message payload.
        message = messaging.Message(
        notification=messaging.Notification(title='title', body='body'),
        data={
        'score': '850',
        'time': '2:45',
        },
        token=registration_token,
        )

        # Send a message to the device corresponding to the provided
        # registration token.
        response = messaging.send(message)
        return Response(response,status=200)
        # Response is a message ID string.
        print('Successfully sent message:', response)

    except Exception as e:
        return Response(str(e),status=400)

