"""
YOVO Marketplace Models
"""

from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    user       = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio        = models.TextField(blank=True)
    avatar     = models.ImageField(upload_to='avatars/', blank=True, null=True)
    location   = models.CharField(max_length=100, blank=True)
    phone      = models.CharField(max_length=20, blank=True)
    address    = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"


class Item(models.Model):
    CATEGORY_CHOICES = [('clothes','Clothes'),('books','Books')]
    LOCATION_CHOICES = [
        ('mumbai','Mumbai'),('delhi','Delhi'),('bangalore','Bangalore'),
        ('chennai','Chennai'),('hyderabad','Hyderabad'),('kolkata','Kolkata'),
        ('pune','Pune'),('ahmedabad','Ahmedabad'),('jaipur','Jaipur'),
        ('surat','Surat'),('other','Other'),
    ]
    CONDITION_CHOICES = [
        ('new','New / Never Used'),('like_new','Like New'),
        ('good','Good'),('fair','Fair'),('worn','Heavily Used'),
    ]
    CONDITION_COLORS = {
        'new':'#3a9c68','like_new':'#3a78c8',
        'good':'#c8773a','fair':'#f59e0b','worn':'#9c988f',
    }

    title       = models.CharField(max_length=200)
    description = models.TextField()
    price       = models.DecimalField(max_digits=10, decimal_places=2)
    category    = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    location    = models.CharField(max_length=50, choices=LOCATION_CHOICES)
    condition   = models.CharField(max_length=20, choices=CONDITION_CHOICES, default='good')
    image       = models.ImageField(upload_to='items/', blank=True, null=True)
    bill        = models.ImageField(upload_to='bills/', blank=True, null=True)
    seller      = models.ForeignKey(User, on_delete=models.CASCADE, related_name='items')
    created_at  = models.DateTimeField(auto_now_add=True)
    is_sold     = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - Rs.{self.price}"

    def get_all_images(self):
        imgs = []
        if self.image:
            imgs.append({'url': self.image.url, 'name': 'Main photo'})
        for ex in self.extra_images.all():
            imgs.append({'url': ex.image.url, 'name': f'Photo {ex.order + 1}'})
        return imgs

    def get_condition_color(self):
        return self.CONDITION_COLORS.get(self.condition, '#9c988f')


class ItemImage(models.Model):
    item  = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='extra_images')
    image = models.ImageField(upload_to='items/extra/')
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"Photo {self.order} of {self.item.title}"


class Cart(models.Model):
    user       = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Cart of {self.user.username}"

    def get_total(self):
        return sum(ci.item.price * ci.quantity for ci in self.cart_items.all())

    def get_item_count(self):
        return sum(ci.quantity for ci in self.cart_items.all())


class CartItem(models.Model):
    cart     = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='cart_items')
    item     = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ('cart', 'item')

    def __str__(self):
        return f"{self.quantity}x {self.item.title}"

    def get_subtotal(self):
        return self.item.price * self.quantity


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending','Pending'),('confirmed','Confirmed'),
        ('shipped','Shipped'),('delivered','Delivered'),('cancelled','Cancelled'),
    ]
    PAYMENT_CHOICES = [
        ('card','Credit/Debit Card'),('upi','UPI'),('cod','Cash on Delivery'),
    ]

    buyer          = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    order_id       = models.CharField(max_length=20, unique=True)
    status         = models.CharField(max_length=20, choices=STATUS_CHOICES, default='confirmed')
    payment_method = models.CharField(max_length=10, choices=PAYMENT_CHOICES, default='cod')
    payment_ref    = models.CharField(max_length=100, blank=True)
    total          = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    delivery_name  = models.CharField(max_length=100, blank=True)
    delivery_phone = models.CharField(max_length=20, blank=True)
    delivery_addr  = models.TextField(blank=True)
    created_at     = models.DateTimeField(auto_now_add=True)
    updated_at     = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Order {self.order_id} by {self.buyer.username}"


class OrderItem(models.Model):
    order    = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_items')
    item     = models.ForeignKey(Item, on_delete=models.SET_NULL, null=True, related_name='order_items')
    seller   = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='sales')
    title    = models.CharField(max_length=200)
    price    = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity}x {self.title}"

    def get_subtotal(self):
        return self.price * self.quantity


class Message(models.Model):
    sender     = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    receiver   = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    item       = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='messages')
    content    = models.TextField()
    timestamp  = models.DateTimeField(auto_now_add=True)
    edited_at  = models.DateTimeField(null=True, blank=True)
    is_read    = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f"{self.sender.username} to {self.receiver.username}: {self.content[:40]}"


class Question(models.Model):
    item        = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='questions')
    asker       = models.ForeignKey(User, on_delete=models.CASCADE, related_name='questions_asked')
    content     = models.TextField()
    answer      = models.TextField(blank=True)
    answered_at = models.DateTimeField(null=True, blank=True)
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Q by {self.asker.username} on {self.item.title[:30]}"

    class Wishlist(models.Model):
        user = models.ForeignKey(
            User, on_delete=models.CASCADE, related_name='wishlists'
        )
        item = models.ForeignKey(
            'Item', on_delete=models.CASCADE, related_name='wishlisted_by'
        )
        added_at = models.DateTimeField(auto_now_add=True)

        class Meta:
            unique_together = ('user', 'item')
            ordering = ['-added_at']

        def __str__(self):
            return f"{self.user.username} ♥ {self.item.title}"