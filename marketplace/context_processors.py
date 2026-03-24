from .models import Cart, Message, ContactMessage


def cart_count(request):
    """Adds cart_count to every template — shows cart badge in navbar."""
    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user).first()
        return {'cart_count': cart.get_item_count() if cart else 0}
    return {'cart_count': 0}


def nav_unread_count(request):
    """Adds nav_unread_count to every template — shows Messages badge in navbar.
    Only counts > 0 are shown. Never shows 0."""
    if request.user.is_authenticated:
        count = Message.objects.filter(
            receiver=request.user,
            is_read=False,
        ).count()
        return {'nav_unread_count': count}
    return {'nav_unread_count': 0}


def unread_contact_count(request):
    """Adds unread_contact_count to every template — shows unread contact
    form submissions. Only visible to staff/admin users."""
    if request.user.is_authenticated and request.user.is_staff:
        count = ContactMessage.objects.filter(is_read=False).count()
        return {'unread_contact_count': count}
    return {'unread_contact_count': 0}