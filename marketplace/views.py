"""
YOVO Marketplace Views — Full Featured
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q, Sum
from django.utils import timezone
from django.views.decorators.http import require_POST
import random, string

from .models import Item, ItemImage, Cart, CartItem, Message, Profile, Order, OrderItem, Question, ContactMessage, Wishlist
from .forms import RegisterForm, LoginForm, ItemForm, ProfileForm, MessageForm


# ─── Home ──────────────────────────────────────────────────────────────────────
def home(request):
    items = Item.objects.filter(is_sold=False).select_related('seller')
    category    = request.GET.get('category', '')
    subcategory = request.GET.get('subcategory', '')
    location    = request.GET.get('location', '')
    condition   = request.GET.get('condition', '')
    min_price   = request.GET.get('min_price', '')
    max_price   = request.GET.get('max_price', '')
    search      = request.GET.get('search', '')

    if category:    items = items.filter(category=category)
    if subcategory: items = items.filter(subcategory=subcategory)
    if location:    items = items.filter(location=location)
    if condition:   items = items.filter(condition=condition)
    if min_price:   items = items.filter(price__gte=min_price)
    if max_price:   items = items.filter(price__lte=max_price)
    if search:      items = items.filter(Q(title__icontains=search) | Q(description__icontains=search))

    wishlist_ids = set()
    if request.user.is_authenticated:
        wishlist_ids = set(Wishlist.objects.filter(user=request.user).values_list('item_id', flat=True))

    return render(request, 'marketplace/home.html', {
        'items':               items,
        'category_choices':    Item.CATEGORY_CHOICES,
        'subcategory_choices': Item.SUBCATEGORY_CHOICES,
        'subcategory_map':     Item.SUBCATEGORY_MAP,
        'location_choices':    Item.LOCATION_CHOICES,
        'condition_choices':   Item.CONDITION_CHOICES,
        'selected_category':   category,
        'selected_subcategory': subcategory,
        'selected_location':   location,
        'selected_condition':  condition,
        'min_price': min_price,
        'max_price': max_price,
        'search':    search,
        'wishlist_ids': wishlist_ids,
    })


# ─── Item Detail ───────────────────────────────────────────────────────────────
def item_detail(request, pk):
    item = get_object_or_404(Item, pk=pk)
    all_images = item.get_all_images()
    related = Item.objects.filter(
        category=item.category, is_sold=False
    ).exclude(pk=pk).select_related('seller')[:4]

    is_wishlisted = False
    if request.user.is_authenticated:
        is_wishlisted = Wishlist.objects.filter(user=request.user, item=item).exists()

    return render(request, 'marketplace/item_detail.html', {
        'item':          item,
        'all_images':    all_images,
        'related':       related,
        'is_wishlisted': is_wishlisted,
    })


# ─── Auth ──────────────────────────────────────────────────────────────────────
def register_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    form = RegisterForm(request.POST or None)
    if form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, f"Welcome to YOVO, {user.first_name or user.username}! 🎉")
        return redirect('home')
    return render(request, 'marketplace/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    form = LoginForm(request, data=request.POST or None)
    if request.POST and form.is_valid():
        user = form.get_user()
        login(request, user)
        return redirect(request.GET.get('next', 'home'))
    return render(request, 'marketplace/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, "You've been logged out. See you soon!")
    return redirect('home')


# ─── Post Item ─────────────────────────────────────────────────────────────────
@login_required
def post_item(request):
    form = ItemForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        item = form.save(commit=False)
        item.seller = request.user
        item.save()
        form.save_extra_images(item)
        messages.success(request, "Your item is now live! 🚀")
        return redirect('item_detail', pk=item.pk)
    return render(request, 'marketplace/post_item.html', {'form': form})


@login_required
def edit_item(request, pk):
    item = get_object_or_404(Item, pk=pk, seller=request.user)
    # Capture originals BEFORE binding POST data
    original_image = item.image.name if item.image else None
    original_bill  = item.bill.name  if item.bill  else None

    form = ItemForm(request.POST or None, request.FILES or None, instance=item)
    form.fields['image'].required = False
    form.fields['bill'].required  = False

    if form.is_valid():
        saved = form.save(commit=False)
        # If no new image uploaded, keep the existing one
        if not request.FILES.get('image'):
            saved.image = original_image or ''
        # If no new bill uploaded, keep the existing one
        if not request.FILES.get('bill'):
            saved.bill = original_bill or ''
        saved.save()
        form.save_extra_images(saved)
        messages.success(request, "Item updated successfully! ✅")
        return redirect('item_detail', pk=item.pk)
    # Pass existing extra images with their PKs for delete links
    extra_images = item.extra_images.all()
    return render(request, 'marketplace/post_item.html', {
        'form': form,
        'item': item,
        'editing': True,
        'existing_images': item.get_all_images(),
        'extra_images_qs': extra_images,   # queryset with real PKs
        'current_condition': item.condition,  # pass current condition explicitly
    })


@login_required
def delete_extra_image(request, image_pk):
    """Delete a single extra image."""
    img = get_object_or_404(ItemImage, pk=image_pk, item__seller=request.user)
    item_pk = img.item.pk
    img.delete()
    messages.success(request, "Photo removed.")
    return redirect('edit_item', pk=item_pk)


@login_required
def mark_sold(request, pk):
    item = get_object_or_404(Item, pk=pk, seller=request.user)
    item.is_sold = True
    item.save()
    messages.success(request, f'"{item.title}" marked as sold.')
    return redirect('dashboard')


@login_required
def delete_item(request, pk):
    item = get_object_or_404(Item, pk=pk, seller=request.user)
    item.delete()
    messages.success(request, "Item deleted.")
    return redirect('dashboard')


# ─── Dashboard ─────────────────────────────────────────────────────────────────
@login_required
def dashboard(request):
    my_items = Item.objects.filter(seller=request.user).order_by('-created_at')
    profile, _ = Profile.objects.get_or_create(user=request.user)
    profile_form = ProfileForm(
        request.POST or None, request.FILES or None,
        instance=profile, user_instance=request.user
    )
    if request.POST and profile_form.is_valid():
        profile_form.save()
        messages.success(request, "Profile updated!")
        return redirect('dashboard')

    total_listings  = my_items.count()
    active_listings = my_items.filter(is_sold=False).count()
    sold_listings   = my_items.filter(is_sold=True).count()
    unread_messages = Message.objects.filter(receiver=request.user, is_read=False).count()

    # Incoming orders (someone bought seller's items)
    # Count BEFORE slicing to avoid filtering a sliced queryset
    incoming_qs = OrderItem.objects.filter(
        seller=request.user
    ).select_related('order', 'order__buyer', 'item').order_by('-order__created_at')
    new_orders_count = incoming_qs.filter(order__status='confirmed').count()
    incoming_orders  = incoming_qs[:10]  # slice AFTER counting

    sent     = Message.objects.filter(sender=request.user).select_related('receiver', 'item')
    received = Message.objects.filter(receiver=request.user).select_related('sender', 'item')
    conversations = {}
    for msg in list(sent) + list(received):
        other = msg.receiver if msg.sender == request.user else msg.sender
        key   = (msg.item.id, other.id)
        if key not in conversations:
            conversations[key] = {
                'message': msg, 'other_user': other, 'item': msg.item,
                'unread': Message.objects.filter(
                    sender=other, receiver=request.user, item=msg.item, is_read=False
                ).count(),
            }
    conversation_list = sorted(conversations.values(), key=lambda x: x['message'].timestamp, reverse=True)[:10]

    return render(request, 'marketplace/dashboard.html', {
        'my_items':          my_items,
        'profile':           profile,
        'profile_form':      profile_form,
        'total_listings':    total_listings,
        'active_listings':   active_listings,
        'sold_listings':     sold_listings,
        'unread_messages':   unread_messages,
        'conversation_list': conversation_list,
        'incoming_orders':   incoming_orders,
        'new_orders_count':  new_orders_count,
    })


# ─── Edit Profile ──────────────────────────────────────────────────────────────
@login_required
def edit_profile(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    form = ProfileForm(
        request.POST or None, request.FILES or None,
        instance=profile, user_instance=request.user
    )
    if form.is_valid():
        form.save()
        messages.success(request, "✅ Profile updated successfully!")
        return redirect('edit_profile')
    return render(request, 'marketplace/edit_profile.html', {
        'form': form, 'profile': profile,
    })


# ─── Wishlist ──────────────────────────────────────────────────────────────────
@login_required
def wishlist_view(request):
    wishlist_items = Wishlist.objects.filter(user=request.user).select_related('item', 'item__seller')
    return render(request, 'marketplace/wishlist.html', {'wishlist_items': wishlist_items})


@login_required
def toggle_wishlist(request, pk):
    item = get_object_or_404(Item, pk=pk)
    if item.seller == request.user:
        messages.warning(request, "You can't wishlist your own item.")
        return redirect(request.META.get('HTTP_REFERER', 'home'))
    obj, created = Wishlist.objects.get_or_create(user=request.user, item=item)
    if not created:
        obj.delete()
        messages.info(request, f'"{item.title}" removed from wishlist.')
    else:
        messages.success(request, f'"{item.title}" added to wishlist! ♥')
    return redirect(request.META.get('HTTP_REFERER', 'home'))


# ─── Cart ──────────────────────────────────────────────────────────────────────
@login_required
def cart_view(request):
    cart, _ = Cart.objects.get_or_create(user=request.user)
    subtotal = cart.get_total()
    platform_fee = round(subtotal * 12 / 100, 2)
    grand_total = round(subtotal + platform_fee, 2)
    return render(request, 'marketplace/cart.html', {
        'cart': cart,
        'subtotal': subtotal,
        'platform_fee': platform_fee,
        'grand_total': grand_total,
    })


@login_required
def add_to_cart(request, pk):
    item = get_object_or_404(Item, pk=pk, is_sold=False)
    if item.seller == request.user:
        messages.warning(request, "You can't add your own item to cart.")
        return redirect('home')
    cart, _ = Cart.objects.get_or_create(user=request.user)
    cart_item, created = CartItem.objects.get_or_create(cart=cart, item=item)
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    messages.success(request, f'"{item.title}" added to cart!')
    return redirect(request.META.get('HTTP_REFERER', 'home'))


@login_required
def remove_from_cart(request, pk):
    cart_item = get_object_or_404(CartItem, pk=pk, cart__user=request.user)
    cart_item.delete()
    messages.success(request, "Item removed from cart.")
    return redirect('cart')


@login_required
def update_cart(request, pk):
    cart_item = get_object_or_404(CartItem, pk=pk, cart__user=request.user)
    qty = int(request.POST.get('quantity', 1))
    if qty < 1:
        cart_item.delete()
    else:
        cart_item.quantity = qty
        cart_item.save()
    return redirect('cart')


@login_required
def checkout(request):
    cart, _ = Cart.objects.get_or_create(user=request.user)
    if not cart.cart_items.exists():
        messages.warning(request, "Your cart is empty.")
        return redirect('cart')

    if request.method == 'POST':
        # Generate unique order ID
        order_id = 'YV-' + ''.join(random.choices(string.digits, k=6))
        while Order.objects.filter(order_id=order_id).exists():
            order_id = 'YV-' + ''.join(random.choices(string.digits, k=6))

        payment_method  = request.POST.get('payment_method', 'cod')
        payment_ref     = request.POST.get('payment_ref', '')
        subtotal        = cart.get_total()
        COMMISSION_RATE = 12  # 12% platform commission
        commission_fee  = round(subtotal * COMMISSION_RATE / 100, 2)
        total           = round(subtotal + commission_fee, 2)

        # Build full name from first + last name fields
        first_name = request.POST.get('first_name', '').strip()
        last_name  = request.POST.get('last_name', '').strip()
        full_name  = f"{first_name} {last_name}".strip() or request.user.get_full_name() or request.user.username

        # Build address string
        address = request.POST.get('address', '').strip()
        city    = request.POST.get('city', '').strip()
        state   = request.POST.get('state', '').strip()
        pin     = request.POST.get('pin', '').strip()
        delivery_addr = ', '.join(filter(None, [address, city, state]))
        if pin:
            delivery_addr += f' — {pin}'

        order = Order.objects.create(
            buyer          = request.user,
            order_id       = order_id,
            payment_method = payment_method,
            payment_ref    = payment_ref,
            total          = total,
            commission_fee = commission_fee,
            delivery_name  = full_name,
            delivery_phone = request.POST.get('phone', '').strip(),
            delivery_addr  = delivery_addr,
            status         = 'confirmed',
        )

        # Create order items + mark items as sold
        for ci in cart.cart_items.all():
            OrderItem.objects.create(
                order    = order,
                item     = ci.item,
                seller   = ci.item.seller,
                title    = ci.item.title,
                price    = ci.item.price,
                quantity = ci.quantity,
            )
            ci.item.is_sold = True
            ci.item.save()

        # Clear cart
        cart.cart_items.all().delete()

        return redirect('order_detail', order_id=order.order_id)

    profile = getattr(request.user, 'profile', None)
    return render(request, 'marketplace/checkout.html', {
        'cart': cart,
        'profile': profile,
    })


@login_required
def my_orders(request):
    """Buyer: all orders placed."""
    orders = Order.objects.filter(buyer=request.user).prefetch_related('order_items')
    return render(request, 'marketplace/my_orders.html', {'orders': orders})


@login_required
def order_detail(request, order_id):
    """Full order detail — accessible by buyer OR any seller whose item is in the order."""
    try:
        order = Order.objects.filter(
            Q(order_id=order_id) & (
                Q(buyer=request.user) |
                Q(order_items__seller=request.user)
            )
        ).distinct().get()
    except Order.DoesNotExist:
        from django.http import Http404
        raise Http404("Order not found.")

    is_seller_view = order.buyer != request.user
    return render(request, 'marketplace/order_detail.html', {
        'order': order,
        'is_seller_view': is_seller_view,
    })


@login_required
def seller_sales(request):
    """Seller: all sales + earnings. Marks all new orders as seen on visit."""
    from decimal import Decimal

    # Mark all this seller's unseen confirmed orders as seen
    Order.objects.filter(
        order_items__seller=request.user,
        seller_seen=False,
    ).update(seller_seen=True)

    sales = OrderItem.objects.filter(
        seller=request.user
    ).select_related('order', 'item').order_by('-order__created_at')

    total_earned = sales.aggregate(total=Sum('price'))['total'] or 0
    total_commission = sum(o.order.commission_fee for o in sales)
    total_buyer_paid = total_earned + total_commission

    return render(request, 'marketplace/seller_sales.html', {
        'sales': sales,
        'total_earned': total_earned,
        'total_commission': total_commission,
        'total_buyer_paid': total_buyer_paid,
    })


def faq(request):
    """FAQ page."""
    return render(request, 'marketplace/faq.html')

def about(request):
    """About Us page."""
    return render(request, 'marketplace/about.html')

def sustainability(request):
    """Sustainability page."""
    return render(request, 'marketplace/sustainability.html')

def contact(request):
    """Contact page — saves messages to DB on POST."""
    if request.method == 'POST':
        import json
        try:
            data       = json.loads(request.body)
            first_name = data.get('first_name', '').strip()
            last_name  = data.get('last_name', '').strip()
            email      = data.get('email', '').strip()
            subject    = data.get('subject', 'general').strip()
            msg_text   = data.get('message', '').strip()

            if not first_name or not email or not subject or not msg_text:
                return JsonResponse({'ok': False, 'error': 'Missing required fields.'}, status=400)

            ContactMessage.objects.create(
                first_name=first_name,
                last_name=last_name,
                email=email,
                subject=subject,
                message=msg_text,
            )
            return JsonResponse({'ok': True})
        except Exception as e:
            return JsonResponse({'ok': False, 'error': str(e)}, status=500)

    return render(request, 'marketplace/contact.html')


# ─── Category Page ─────────────────────────────────────────────────────────────
def category_page(request, category_slug):
    CATEGORY_META = {
        'clothes': {
            'label':   'Clothes',
            'emoji':   '👗',
            'tagline': 'Pre-loved fashion for every style',
            'desc':    'Browse second-hand tops, jeans, dresses, jackets and more. Quality fashion at a fraction of the price.',
            'subcategories': [
                {'slug':'tops',       'label':'Tops',       'emoji':'👕'},
                {'slug':'shirts',     'label':'Shirts',     'emoji':'👔'},
                {'slug':'jeans',      'label':'Jeans',      'emoji':'👖'},
                {'slug':'dresses',    'label':'Dresses',    'emoji':'👗'},
                {'slug':'jackets',    'label':'Jackets',    'emoji':'🧥'},
                {'slug':'ethnic',     'label':'Ethnic',     'emoji':'🥻'},
                {'slug':'activewear', 'label':'Activewear', 'emoji':'🏃'},
                {'slug':'winterwear', 'label':'Winterwear', 'emoji':'🧤'},
            ],
        },
        'books': {
            'label':   'Books',
            'emoji':   '📚',
            'tagline': 'Knowledge should be shared, not wasted',
            'desc':    'Discover fiction, textbooks, non-fiction and more. Give books a second life and save big on your reads.',
            'subcategories': [
                {'slug':'fiction',    'label':'Fiction',    'emoji':'📖'},
                {'slug':'nonfiction', 'label':'Non-Fiction', 'emoji':'📰'},
                {'slug':'textbooks',  'label':'Textbooks',  'emoji':'🎓'},
                {'slug':'children',   'label':"Children's", 'emoji':'🧸'},
                {'slug':'comics',     'label':'Comics',     'emoji':'💥'},
                {'slug':'selfhelp',   'label':'Self-Help',  'emoji':'💡'},
                {'slug':'biography',  'label':'Biography',  'emoji':'🧑'},
                {'slug':'science',    'label':'Science',    'emoji':'🔬'},
            ],
        },
        'accessories': {
            'label':   'Accessories',
            'emoji':   '👜',
            'tagline': 'Find unique pieces, own your style',
            'desc':    'Bags, jewellery, watches, belts, sunglasses and more. One person\'s shelf item is your next favourite thing.',
            'subcategories': [
                {'slug':'bags',       'label':'Bags',       'emoji':'👜'},
                {'slug':'jewellery',  'label':'Jewellery',  'emoji':'💍'},
                {'slug':'watches',    'label':'Watches',    'emoji':'⌚'},
                {'slug':'belts',      'label':'Belts',      'emoji':'🔗'},
                {'slug':'sunglasses', 'label':'Sunglasses', 'emoji':'🕶️'},
                {'slug':'footwear',   'label':'Footwear',   'emoji':'👟'},
                {'slug':'caps',       'label':'Caps',       'emoji':'🧢'},
                {'slug':'scarves',    'label':'Scarves',    'emoji':'🧣'},
            ],
        },
    }

    if category_slug not in CATEGORY_META:
        from django.http import Http404
        raise Http404("Category not found")

    meta = CATEGORY_META[category_slug]
    subcategory   = request.GET.get('subcategory', '')
    location      = request.GET.get('location', '')
    condition     = request.GET.get('condition', '')
    min_price     = request.GET.get('min_price', '')
    max_price     = request.GET.get('max_price', '')
    search        = request.GET.get('search', '')

    items = Item.objects.filter(is_sold=False, category=category_slug).select_related('seller')
    total_count = items.count()

    if subcategory: items = items.filter(subcategory=subcategory)
    if location:    items = items.filter(location=location)
    if condition:   items = items.filter(condition=condition)
    if min_price:   items = items.filter(price__gte=min_price)
    if max_price:   items = items.filter(price__lte=max_price)
    if search:      items = items.filter(Q(title__icontains=search) | Q(description__icontains=search))

    # Get subcategory label for breadcrumb
    sub_label = ''
    if subcategory:
        sub_label = next((s['label'] for s in meta['subcategories'] if s['slug'] == subcategory), subcategory)

    wishlist_ids = set()
    if request.user.is_authenticated:
        wishlist_ids = set(Wishlist.objects.filter(user=request.user).values_list('item_id', flat=True))

    return render(request, 'marketplace/category.html', {
        'items':               items,
        'total_count':         total_count,
        'category_slug':       category_slug,
        'category_label':      meta['label'],
        'category_emoji':      meta['emoji'],
        'hero_tagline':        meta['tagline'],
        'hero_desc':           meta['desc'],
        'subcategories':       meta['subcategories'],
        'selected_subcategory': subcategory,
        'subcategory_label':   sub_label,
        'selected_location':   location,
        'selected_condition':  condition,
        'location_choices':    Item.LOCATION_CHOICES,
        'condition_choices':   Item.CONDITION_CHOICES,
        'min_price':  min_price,
        'max_price':  max_price,
        'search':     search,
        'wishlist_ids': wishlist_ids,
    })


# ─── Chat ──────────────────────────────────────────────────────────────────────
@login_required
def chat_view(request, item_pk, user_pk):
    item       = get_object_or_404(Item, pk=item_pk)
    other_user = get_object_or_404(User, pk=user_pk)

    if request.user != item.seller and other_user != item.seller:
        messages.error(request, "Invalid chat session.")
        return redirect('home')

    # Plain POST fallback
    if request.method == 'POST':
        content = request.POST.get('content', '').strip()
        if content:
            Message.objects.create(
                sender=request.user, receiver=other_user,
                item=item, content=content,
            )
        return redirect('chat', item_pk=item_pk, user_pk=user_pk)

    chat_messages = Message.objects.filter(
        item=item, is_deleted=False
    ).filter(
        Q(sender=request.user, receiver=other_user) |
        Q(sender=other_user,   receiver=request.user)
    ).order_by('timestamp')

    chat_messages.filter(receiver=request.user, is_read=False).update(is_read=True)

    return render(request, 'marketplace/chat.html', {
        'item':          item,
        'other_user':    other_user,
        'chat_messages': chat_messages,
        'room_name':     f"item_{item_pk}_users_{min(request.user.pk, other_user.pk)}_{max(request.user.pk, other_user.pk)}",
    })


@login_required
def edit_message(request, msg_pk):
    """Edit a chat message (AJAX POST)."""
    msg = get_object_or_404(Message, pk=msg_pk, sender=request.user)
    if request.method == 'POST':
        new_content = request.POST.get('content', '').strip()
        if new_content:
            msg.content   = new_content
            msg.edited_at = timezone.now()
            msg.save()
            return JsonResponse({'success': True, 'content': msg.content})
    return JsonResponse({'success': False})


@login_required
def delete_message(request, msg_pk):
    """Soft-delete a chat message."""
    msg = get_object_or_404(Message, pk=msg_pk, sender=request.user)
    msg.is_deleted = True
    msg.content    = "This message was deleted."
    msg.save()
    return JsonResponse({'success': True})


# ─── Inbox ─────────────────────────────────────────────────────────────────────
@login_required
def inbox(request):
    sent     = Message.objects.filter(sender=request.user).select_related('receiver', 'item')
    received = Message.objects.filter(receiver=request.user).select_related('sender', 'item')
    conversations = {}
    for msg in list(sent) + list(received):
        other = msg.receiver if msg.sender == request.user else msg.sender
        key   = (msg.item.id, other.id)
        if key not in conversations or msg.timestamp > conversations[key]['message'].timestamp:
            conversations[key] = {
                'message': msg, 'other_user': other, 'item': msg.item,
                'unread': Message.objects.filter(
                    sender=other, receiver=request.user, item=msg.item, is_read=False
                ).count(),
            }
    conversation_list = sorted(conversations.values(), key=lambda x: x['message'].timestamp, reverse=True)
    return render(request, 'marketplace/inbox.html', {'conversation_list': conversation_list})


@login_required
def ask_question(request, item_pk):
    """Buyer asks a question on an item."""
    item = get_object_or_404(Item, pk=item_pk)
    if request.method == 'POST':
        content = request.POST.get('content', '').strip()
        if content:
            Question.objects.create(item=item, asker=request.user, content=content)
            messages.success(request, "✅ Your question has been posted!")
        else:
            messages.error(request, "Question cannot be empty.")
    return redirect('item_detail', pk=item_pk)


@login_required
def answer_question(request, q_pk):
    """Seller answers a question."""
    question = get_object_or_404(Question, pk=q_pk, item__seller=request.user)
    if request.method == 'POST':
        answer = request.POST.get('answer', '').strip()
        if answer:
            question.answer      = answer
            question.answered_at = timezone.now()
            question.save()
            messages.success(request, "✅ Answer posted!")
    return redirect('item_detail', pk=question.item.pk)


@login_required
def delete_question(request, q_pk):
    """Delete a question (asker or seller)."""
    question = get_object_or_404(Question, pk=q_pk)
    item_pk  = question.item.pk
    if request.user == question.asker or request.user == question.item.seller:
        question.delete()
    return redirect('item_detail', pk=item_pk)


# ─── User Profile ──────────────────────────────────────────────────────────────
def user_profile(request, username):
    profile_user = get_object_or_404(User, username=username)
    items = Item.objects.filter(seller=profile_user, is_sold=False)
    return render(request, 'marketplace/user_profile.html', {
        'profile_user': profile_user,
        'items':        items,
    })


# ─── Error Handlers ────────────────────────────────────────────────────────────
def handler404(request, exception=None):
    return render(request, '404.html', status=404)

def handler500(request):
    return render(request, '404.html', status=500)

# ─── Unread Count API ──────────────────────────────────────────────────────────
@login_required
def unread_count(request):
    """Returns total unread message count for current user as JSON.
    Used by frontend polling to keep nav badge and dashboard fresh."""
    count = Message.objects.filter(receiver=request.user, is_read=False).count()
    return JsonResponse({'count': count})


# ─── 3. ADD these two new API views (add at the bottom of views.py) ──────────

@login_required
def unread_count(request):
    """Returns total unread message count as JSON for nav badge polling."""
    count = Message.objects.filter(receiver=request.user, is_read=False).count()
    return JsonResponse({'count': count})


@login_required
def new_orders_count_api(request):
    """Returns count of new (unseen) confirmed orders for this seller."""
    count = OrderItem.objects.filter(
        seller=request.user,
        order__status='confirmed',
        order__seller_seen=False,
    ).values('order').distinct().count()
    return JsonResponse({'count': count})


@login_required
@require_POST
def mark_sales_seen(request):
    """Marks all confirmed orders for this seller as seen. Called via AJAX."""
    updated = Order.objects.filter(
        order_items__seller=request.user,
        seller_seen=False,
    ).update(seller_seen=True)
    return JsonResponse({'ok': True, 'updated': updated})
