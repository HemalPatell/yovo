from django.contrib import admin
from django.utils.html import format_html, mark_safe
from django.utils.timezone import localtime
from .models import (
    Profile, Item, ItemImage,
    Cart, CartItem,
    Order, OrderItem,
    Message, Question,
    ContactMessage,
)


# ── Contact Message Admin ───────────────────────────────────────────────────────

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display  = ['notification_dot', 'first_name', 'last_name', 'email_link',
                     'subject_badge', 'msg_preview', 'received_at', 'read_status']
    list_filter   = ['is_read', 'subject', 'created_at']
    search_fields = ['first_name', 'last_name', 'email', 'message']
    readonly_fields = ['first_name', 'last_name', 'email', 'subject',
                       'message_display', 'created_at']
    actions       = ['mark_as_read', 'mark_as_unread']
    ordering      = ['-created_at']

    fieldsets = (
        ('📨 Contact Details', {
            'fields': ('first_name', 'last_name', 'email', 'subject'),
        }),
        ('💬 Message', {
            'fields': ('message_display',),
        }),
        ('📋 Status', {
            'fields': ('is_read', 'created_at'),
        }),
    )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # Auto-mark as read when admin opens the list
        return qs

    def changeform_view(self, request, object_id=None, form_url='', extra_context=None):
        """Auto-mark as read when admin opens a message."""
        if object_id:
            ContactMessage.objects.filter(pk=object_id).update(is_read=True)
        return super().changeform_view(request, object_id, form_url, extra_context)

    def notification_dot(self, obj):
        if not obj.is_read:
            return format_html(
                '<span style="display:inline-block;width:10px;height:10px;'
                'border-radius:50%;background:#e85050;'
                'box-shadow:0 0 6px rgba(232,80,80,.7);"></span>'
            )
        return format_html('<span style="display:inline-block;width:10px;height:10px;"></span>')
    notification_dot.short_description = ''

    def email_link(self, obj):
        return format_html('<a href="mailto:{}">{}</a>', obj.email, obj.email)
    email_link.short_description = 'Email'

    def subject_badge(self, obj):
        colors = {
            'order':       '#e85050',
            'report':      '#e85050',
            'account':     '#f59e0b',
            'listing':     '#f59e0b',
            'general':     '#5080e8',
            'feature':     '#3acf80',
            'partnership': '#9b59b6',
            'other':       '#888',
        }
        c = colors.get(obj.subject, '#888')
        return format_html(
            '<span style="color:{c};background:{c}22;border:1px solid {c}44;'
            'padding:2px 10px;border-radius:20px;font-size:.73rem;font-weight:700">'
            '{label}</span>',
            c=c, label=obj.get_subject_display())
    subject_badge.short_description = 'Subject'

    def msg_preview(self, obj):
        t = obj.message[:60] + '…' if len(obj.message) > 60 else obj.message
        return format_html('<span style="color:#aaa;font-size:.82rem">{}</span>', t)
    msg_preview.short_description = 'Message'

    def received_at(self, obj):
        return localtime(obj.created_at).strftime('%d %b %Y, %I:%M %p')
    received_at.short_description = 'Received'

    def read_status(self, obj):
        if obj.is_read:
            return mark_safe('<span style="color:#3acf80;font-weight:700">✓ Read</span>')
        return mark_safe('<span style="color:#e85050;font-weight:700">● New</span>')
    read_status.short_description = 'Status'

    def message_display(self, obj):
        return format_html(
            '<div style="background:#1a1a1a;border:1px solid #333;border-radius:8px;'
            'padding:16px;line-height:1.75;white-space:pre-wrap;font-size:.9rem;">{}</div>',
            obj.message)
    message_display.short_description = 'Message'

    @admin.action(description='✓ Mark selected as Read')
    def mark_as_read(self, request, queryset):
        queryset.update(is_read=True)

    @admin.action(description='● Mark selected as Unread')
    def mark_as_unread(self, request, queryset):
        queryset.update(is_read=False)

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        unread = ContactMessage.objects.filter(is_read=False).count()
        extra_context['unread_count'] = unread
        return super().changelist_view(request, extra_context=extra_context)




@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display  = ['user', 'phone', 'location', 'created_at']
    search_fields = ['user__username', 'user__email', 'phone']
    readonly_fields = ['created_at']


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display  = ['item_photo', 'title', 'seller', 'price',
                     'category', 'condition', 'location', 'is_sold', 'created_at']
    list_filter   = ['category', 'condition', 'is_sold', 'location']
    search_fields = ['title', 'description', 'seller__username']
    readonly_fields = ['created_at']   # <-- item_photo NOT here, only in list_display

    def item_photo(self, obj):
        if obj.pk and obj.image:
            return format_html(
                '<img src="{}" width="44" height="44" '
                'style="object-fit:cover;border-radius:7px;border:1px solid #333"/>',
                obj.image.url)
        return '🛍'
    item_photo.short_description = ''


@admin.register(ItemImage)
class ItemImageAdmin(admin.ModelAdmin):
    list_display  = ['item', 'order']
    search_fields = ['item__title']


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display  = ['user', 'created_at']
    search_fields = ['user__username']
    readonly_fields = ['created_at']


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display  = ['cart', 'item', 'quantity']
    search_fields = ['cart__user__username', 'item__title']


class OrderItemInline(admin.TabularInline):
    model      = OrderItem
    extra      = 0
    fields     = ['title', 'seller', 'price', 'quantity']
    readonly_fields = ['title', 'seller', 'price', 'quantity']
    can_delete = False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display  = ['order_id', 'buyer', 'buyer_phone', 'status_badge',
                     'payment_method', 'subtotal_display', 'commission_display', 'total', 'created_at']
    list_filter   = ['status', 'payment_method']
    search_fields = ['order_id', 'buyer__username',
                     'delivery_name', 'delivery_phone']
    readonly_fields = ['order_id', 'created_at', 'updated_at']
    inlines       = [OrderItemInline]
    fieldsets = (
        ('Order Info', {
            'fields': ('order_id', 'buyer', 'status',
                       'total', 'commission_fee', 'created_at', 'updated_at'),
        }),
        ('Payment', {
            'fields': ('payment_method', 'payment_ref'),
        }),
        ('📦 Delivery / Customer Address', {
            'fields': ('delivery_name', 'delivery_phone', 'delivery_addr'),
        }),
    )

    def buyer_phone(self, obj):
        return obj.delivery_phone or '—'
    buyer_phone.short_description = 'Phone'

    def subtotal_display(self, obj):
        subtotal = obj.total - obj.commission_fee
        return format_html('<span style="color:#888">₹{}</span>', subtotal)
    subtotal_display.short_description = 'Subtotal'

    def commission_display(self, obj):
        return format_html(
            '<span style="color:var(--accent);background:rgba(200,119,58,.1);padding:2px 8px;border-radius:6px;font-weight:700;">₹{}</span>',
            obj.commission_fee)
    commission_display.short_description = 'Commission (12%)'

    def status_badge(self, obj):
        colors = {
            'pending':   '#f59e0b',
            'confirmed': '#5080e8',
            'shipped':   '#e8853a',
            'delivered': '#3acf80',
            'cancelled': '#e85050',
        }
        c = colors.get(obj.status, '#888')
        label = obj.get_status_display()
        return format_html(
            '<span style="color:{c};background:{c}22;border:1px solid {c}44;'
            'padding:3px 12px;border-radius:20px;font-size:.73rem;font-weight:700">'
            '{label}</span>',
            c=c, label=label)
    status_badge.short_description = 'Status'


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display  = ['title', 'seller', 'buyer_name', 'buyer_address',
                     'buyer_phone', 'order_link', 'price', 'quantity', 'commission_info', 'order_status']
    search_fields = ['title', 'order__order_id', 'seller__username',
                     'order__buyer__username', 'order__delivery_name', 'order__delivery_phone']
    list_filter   = ['order__status', 'order__payment_method']
    readonly_fields = ['order', 'item', 'seller', 'title', 'price', 'quantity']

    def buyer_name(self, obj):
        return obj.order.delivery_name or obj.order.buyer.get_full_name() or obj.order.buyer.username
    buyer_name.short_description = 'Buyer Name'

    def buyer_address(self, obj):
        return obj.order.delivery_addr or '—'
    buyer_address.short_description = 'Delivery Address'

    def buyer_phone(self, obj):
        return obj.order.delivery_phone or '—'
    buyer_phone.short_description = 'Phone'

    def order_link(self, obj):
        return format_html(
            '<a href="/admin/marketplace/order/?q={}">{}</a>',
            obj.order.order_id, obj.order.order_id)
    order_link.short_description = 'Order ID'

    def commission_info(self, obj):
        return format_html(
            '<span style="font-size:.75rem;color:var(--accent);">₹{}</span>',
            obj.order.commission_fee)
    commission_info.short_description = '12% Fee'

    def order_status(self, obj):
        colors = {
            'pending': '#f59e0b', 'confirmed': '#5080e8',
            'shipped': '#e8853a', 'delivered': '#3acf80', 'cancelled': '#e85050',
        }
        c = colors.get(obj.order.status, '#888')
        return format_html(
            '<span style="color:{};font-weight:700">{}</span>',
            c, obj.order.get_status_display())
    order_status.short_description = 'Status'


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display  = ['sender', 'receiver', 'item',
                     'msg_preview', 'timestamp', 'is_read', 'is_deleted']
    list_filter   = ['is_read', 'is_deleted']
    search_fields = ['sender__username', 'receiver__username', 'content']
    readonly_fields = ['timestamp', 'edited_at']

    def msg_preview(self, obj):
        if obj.is_deleted:
            return mark_safe('<em style="color:#666">Deleted</em>')
        t = obj.content[:55] + '…' if len(obj.content) > 55 else obj.content
        return format_html('<span style="color:#999">{}</span>', t)
    msg_preview.short_description = 'Message'


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display  = ['asker', 'item', 'q_preview', 'is_answered', 'created_at']
    search_fields = ['asker__username', 'content', 'item__title']
    readonly_fields = ['created_at', 'answered_at']

    def q_preview(self, obj):
        t = obj.content[:60] + '…' if len(obj.content) > 60 else obj.content
        return format_html('<span style="color:#999">{}</span>', t)
    q_preview.short_description = 'Question'

    def is_answered(self, obj):
        if obj.answer:
            return mark_safe('<b style="color:#3acf80">✓ Yes</b>')
        return mark_safe('<span style="color:#e85050">✗ No</span>')
    is_answered.short_description = 'Answered?'
