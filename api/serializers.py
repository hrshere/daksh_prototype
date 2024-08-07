from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Category, Shape, Material, Rating, Product, ProductImage, Cart, CartItem, Order, OrderProduct
# utils.py or in your views.py

from django.core.mail import send_mail
from django.conf import settings

def send_order_confirmation_email(user_email, order_details):
    subject = 'Order Confirmation'
    message = f"""
    Dear Customer,

    Thank you for your purchase!

    Order Details:
    Total Quantity: {order_details['total_quantity']}
    Total Price: ${order_details['total_price']}
    Order Products:
    """
    for product in order_details['order_products']:
        message += f"- Product Name: {product['product']}, Quantity: {product['quantity']}\n"# i want to send product ids too for unique identification of products

    message += "\nThank you for shopping with us!"

    send_mail(
        subject,
        message,
        settings.EMAIL_HOST_USER,
        [user_email],
        fail_silently=False,
    )


# Category Serializer
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

# Shape Serializer
class ShapeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shape
        fields = '__all__'

# Material Serializer
class MaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Material
        fields = '__all__'

# Rating Serializer
class RatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rating
        fields = '__all__'

# Product Image Serializer
class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'image']

# Description Serializer
class DescriptionSerializer(serializers.Serializer):
    Dispatch_time = serializers.CharField(max_length=200, allow_blank=True, required=False)
    Suitable_for = serializers.CharField(max_length=200, allow_blank=True, required=False)
    Care_Instructions = serializers.CharField(max_length=200, allow_blank=True, required=False)
    Note = serializers.CharField(max_length=200, allow_blank=True, required=False)

# Product Serializer
class ProductSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)
    category_name = serializers.SerializerMethodField()
    shape_name = serializers.SerializerMethodField()
    material_name = serializers.SerializerMethodField()
    rating_value = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id', 'category', 'category_name', 'shape', 'shape_name', 'material',
            'material_name', 'rating', 'rating_value', 'price', 'minimum_quantity', 
            'name', 'size', 'weight', 'discount_price', 'description', 
            'discount_percent', 'images'
        ]

    def get_category_name(self, obj):
        return obj.category.name

    def get_shape_name(self, obj):
        return obj.shape.name

    def get_material_name(self, obj):
        return obj.material.name

    def get_rating_value(self, obj):
        return obj.rating.value

    def create(self, validated_data):
        description_data = validated_data.pop('description')
        images_data = self.context['request'].FILES.getlist('images')
        product = Product.objects.create(**validated_data)
        product.description = description_data
        for image_data in images_data:
            ProductImage.objects.create(product=product, image=image_data)
        product.save()
        return product

    def update(self, instance, validated_data):
        description_data = validated_data.pop('description', None)
        images_data = self.context['request'].FILES.getlist('images')
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if description_data:
            instance.description = description_data
        if images_data:
            instance.images.all().delete()
            for image_data in images_data:
                ProductImage.objects.create(product=instance, image=image_data)
        instance.save()
        return instance


class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer()

    class Meta:
        model = CartItem
        fields = ['id', 'product', 'quantity', 'total_price']

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)

    class Meta:
        model = Cart
        fields = ['id', 'user', 'items', 'created_at', 'updated_at']

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email']

class OrderProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderProduct
        fields = ['product', 'quantity']

class OrderSerializer(serializers.ModelSerializer):
    order_products = OrderProductSerializer(many=True)
    user_email = serializers.EmailField(write_only=True)  # Use email to identify the user

    class Meta:
        model = Order
        fields = ['user_email', 'total_quantity', 'total_price', 'order_products']

    def create(self, validated_data):
        order_products_data = validated_data.pop('order_products')
        user_email = validated_data.pop('user_email')
        
        # Retrieve or create user based on email
# Check if user exists or create a new one
        user, created = User.objects.get_or_create(
            email=user_email,
            defaults={
                'username': user_email,  # Set username if not provided
                'password': User.objects.make_random_password()  # Or set a default password
            }
        )

        if created:
            # Optionally set a default password if creating a new user
            user.set_password('default_password')  # Ensure to use a proper default password mechanism
            user.save()        
        # Create the order
        order = Order.objects.create(user=user, **validated_data)
        
        # Create associated OrderProducts
        for order_product_data in order_products_data:
            OrderProduct.objects.create(order=order, **order_product_data)

        order_details = {
            'total_quantity': order.total_quantity,
            'total_price': order.total_price,
            'order_products': order_products_data
        }
        send_order_confirmation_email(user_email, order_details)
        
        return order

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['user_email'] = instance.user.email  # Add user email to the output
        return representation