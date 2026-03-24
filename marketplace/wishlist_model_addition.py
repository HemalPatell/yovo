"""
WISHLIST MODEL — Add this class to your marketplace/models.py file.
Place it after your existing model imports and before or after your other models.
Then run: python manage.py makemigrations && python manage.py migrate
"""

# Add this to your marketplace/models.py:

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
