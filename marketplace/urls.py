from django.urls import path
from . import views

urlpatterns = [
    # ── Home & Browse ──────────────────────────────────────────────────
    path('',                            views.home,              name='home'),
    path('item/<int:pk>/',              views.item_detail,       name='item_detail'),
    path('category/<slug:category_slug>/', views.category_page,  name='category'),

    # ── Auth ───────────────────────────────────────────────────────────
    path('register/',                   views.register_view,     name='register'),
    path('login/',                      views.login_view,        name='login'),
    path('logout/',                     views.logout_view,       name='logout'),

    # ── Items ──────────────────────────────────────────────────────────
    path('sell/',                       views.post_item,         name='post_item'),
    path('item/<int:pk>/edit/',         views.edit_item,         name='edit_item'),
    path('item/<int:pk>/delete/',       views.delete_item,       name='delete_item'),
    path('item/<int:pk>/mark-sold/',    views.mark_sold,         name='mark_sold'),
    path('image/<int:image_pk>/delete/',views.delete_extra_image,name='delete_extra_image'),

    # ── Cart ───────────────────────────────────────────────────────────
    path('cart/',                       views.cart_view,         name='cart'),
    path('cart/add/<int:pk>/',          views.add_to_cart,       name='add_to_cart'),
    path('cart/remove/<int:pk>/',       views.remove_from_cart,  name='remove_from_cart'),
    path('cart/update/<int:pk>/',       views.update_cart,       name='update_cart'),
    path('checkout/',                   views.checkout,          name='checkout'),

    # ── Wishlist ───────────────────────────────────────────────────────
    path('wishlist/',                   views.wishlist_view,     name='wishlist'),
    path('wishlist/toggle/<int:pk>/',   views.toggle_wishlist,   name='toggle_wishlist'),

    # ── Orders ─────────────────────────────────────────────────────────
    path('orders/',                     views.my_orders,         name='my_orders'),
    path('orders/<str:order_id>/',      views.order_detail,      name='order_detail'),
    path('sales/',                      views.seller_sales,      name='seller_sales'),

    # ── Dashboard & Profile ────────────────────────────────────────────
    path('dashboard/',                  views.dashboard,         name='dashboard'),
    path('profile/edit/',               views.edit_profile,      name='edit_profile'),
    path('profile/<str:username>/',     views.user_profile,      name='user_profile'),

    # ── Messages ───────────────────────────────────────────────────────
    path('inbox/',                      views.inbox,             name='inbox'),
    path('chat/<int:item_pk>/<int:user_pk>/', views.chat_view,  name='chat'),
    path('message/<int:msg_pk>/edit/',  views.edit_message,      name='edit_message'),
    path('message/<int:msg_pk>/delete/',views.delete_message,    name='delete_message'),

    # ── Q & A ──────────────────────────────────────────────────────────
    path('item/<int:item_pk>/ask/',     views.ask_question,      name='ask_question'),
    path('question/<int:q_pk>/answer/', views.answer_question,   name='answer_question'),
    path('question/<int:q_pk>/delete/', views.delete_question,   name='delete_question'),

    # ── API endpoints ──────────────────────────────────────────────────
    path('api/unread-count/',            views.unread_count,        name='unread_count'),
    path('api/new-orders-count/',        views.new_orders_count_api,name='new_orders_count_api'),
    path('api/mark-sales-seen/',         views.mark_sales_seen,     name='mark_sales_seen'),

    # ── Static Pages ───────────────────────────────────────────────────
    path('faq/',                        views.faq,               name='faq'),
    path('about/',                      views.about,             name='about'),
    path('sustainability/',             views.sustainability,     name='sustainability'),
    path('contact/',                    views.contact,           name='contact'),
]