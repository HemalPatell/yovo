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
    CATEGORY_CHOICES = [
        ('clothes',      'Clothes'),
        ('books',        'Books'),
        ('accessories',  'Accessories'),
    ]

    # Subcategories grouped by parent category
    SUBCATEGORY_CHOICES = [
        # Clothes
        ('tops',        'Tops & T-Shirts'),
        ('shirts',      'Shirts & Blouses'),
        ('jeans',       'Jeans & Trousers'),
        ('dresses',     'Dresses & Skirts'),
        ('jackets',     'Jackets & Coats'),
        ('ethnic',      'Ethnic & Traditional'),
        ('activewear',  'Activewear & Sportswear'),
        ('winterwear',  'Winterwear & Sweaters'),
        # Books
        ('fiction',     'Fiction & Novels'),
        ('nonfiction',  'Non-Fiction'),
        ('textbooks',   'Textbooks & Academic'),
        ('children',    "Children's Books"),
        ('comics',      'Comics & Graphic Novels'),
        ('selfhelp',    'Self-Help & Motivation'),
        ('biography',   'Biography & Memoir'),
        ('science',     'Science & Technology'),
        # Accessories
        ('bags',        'Bags & Backpacks'),
        ('jewellery',   'Jewellery & Rings'),
        ('watches',     'Watches'),
        ('belts',       'Belts & Wallets'),
        ('sunglasses',  'Sunglasses & Eyewear'),
        ('footwear',    'Footwear & Shoes'),
        ('caps',        'Caps & Hats'),
        ('scarves',     'Scarves & Stoles'),
    ]

    SUBCATEGORY_MAP = {
        'clothes':     ['tops','shirts','jeans','dresses','jackets','ethnic','activewear','winterwear'],
        'books':       ['fiction','nonfiction','textbooks','children','comics','selfhelp','biography','science'],
        'accessories': ['bags','jewellery','watches','belts','sunglasses','footwear','caps','scarves'],
    }
    LOCATION_CHOICES = [
        ('mumbai',    'Mumbai'),
        ('delhi',     'Delhi'),
        ('bangalore', 'Bangalore'),
        ('chennai',   'Chennai'),
        ('hyderabad', 'Hyderabad'),
        ('kolkata',   'Kolkata'),
        ('pune',      'Pune'),
        ('ahmedabad', 'Ahmedabad'),
        ('jaipur',    'Jaipur'),
        ('surat',     'Surat'),
        ('other',     'Other'),
    ]
    CONDITION_CHOICES = [
        ('new',      'New / Never Used'),
        ('like_new', 'Like New'),
        ('good',     'Good'),
        ('fair',     'Fair'),
        ('worn',     'Heavily Used'),
    ]
    GENDER_CHOICES = [
        ('men',    'Men'),
        ('women',  'Women'),
        ('unisex', 'Unisex'),
        ('kids',   'Kids'),
    ]
    GENDER_ICONS = {
        'men':    '👨',
        'women':  '👩',
        'unisex': '🤝',
        'kids':   '🧒',
    }

    CONDITION_COLORS = {
        'new':      '#3a9c68',
        'like_new': '#3a78c8',
        'good':     '#c8773a',
        'fair':     '#f59e0b',
        'worn':     '#9c988f',
    }
    CONDITION_ICONS = {
        'new':      '✨',
        'like_new': '🌟',
        'good':     '👍',
        'fair':     '👌',
        'worn':     '🔧',
    }

    title       = models.CharField(max_length=200)
    description = models.TextField()
    price       = models.DecimalField(max_digits=10, decimal_places=2)
    category    = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    subcategory = models.CharField(max_length=20, choices=SUBCATEGORY_CHOICES, blank=True, default='')
    gender      = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True, default='')
    location    = models.CharField(max_length=50, choices=LOCATION_CHOICES)
    condition   = models.CharField(max_length=20, choices=CONDITION_CHOICES, default='good')
    image       = models.ImageField(upload_to='items/', blank=True, null=True)
    bill        = models.ImageField(upload_to='bills/', blank=True, null=True,
                                    help_text='Optional: upload bill/receipt for authenticity')
    seller      = models.ForeignKey(User, on_delete=models.CASCADE, related_name='items')
    created_at  = models.DateTimeField(auto_now_add=True)
    is_sold     = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} — Rs.{self.price}"

    def get_all_images(self):
        imgs = []
        if self.image:
            imgs.append({'url': self.image.url, 'name': 'Main photo'})
        for ex in self.extra_images.all():
            imgs.append({'url': ex.image.url, 'name': f'Photo {ex.order + 1}'})
        return imgs

    def get_condition_color(self):
        return self.CONDITION_COLORS.get(self.condition, '#9c988f')

    def get_condition_icon(self):
        return self.CONDITION_ICONS.get(self.condition, '')

    def get_gender_icon(self):
        return self.GENDER_ICONS.get(self.gender, '')


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
        ('pending',   'Pending'),
        ('confirmed', 'Confirmed'),
        ('shipped',   'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]
    PAYMENT_CHOICES = [
        ('card', 'Credit/Debit Card'),
        ('upi',  'UPI'),
        ('cod',  'Cash on Delivery'),
        ('neft', 'Bank Transfer / NEFT'),
    ]

    buyer          = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    order_id       = models.CharField(max_length=20, unique=True)
    status         = models.CharField(max_length=20, choices=STATUS_CHOICES, default='confirmed')
    payment_method = models.CharField(max_length=10, choices=PAYMENT_CHOICES, default='cod')
    payment_ref    = models.CharField(max_length=100, blank=True)
    total          = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    commission_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
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

    def get_subtotal(self):
        return self.price * self.quantity

    def __str__(self):
        return f"{self.quantity}x {self.title}"


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


class ContactMessage(models.Model):
    SUBJECT_CHOICES = [
        ('general',     'General Question'),
        ('order',       'Problem with my order'),
        ('listing',     'Problem with a listing'),
        ('account',     'Account issue'),
        ('report',      'Report a user'),
        ('feature',     'Feature request'),
        ('partnership', 'Partnership inquiry'),
        ('other',       'Other'),
    ]

    first_name = models.CharField(max_length=100)
    last_name  = models.CharField(max_length=100, blank=True)
    email      = models.EmailField()
    subject    = models.CharField(max_length=20, choices=SUBJECT_CHOICES, default='general')
    message    = models.TextField()
    is_read    = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"[{'✓' if self.is_read else 'NEW'}] {self.get_subject_display()} — {self.first_name} {self.email}"


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
