from django.db import models

class OrderDetail(models.Model):
    class OrderStatus(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        PROCESSING = 'PROCESSING', 'Processing'
        SHIPPED = 'SHIPPED', 'Shipped'
        DELIVERED = 'DELIVERED', 'Delivered'
        CANCELLED = 'CANCELLED', 'Cancelled'

    user = models.CharField(default=True)
    product_name = models.CharField(max_length=260)
    image = models.ImageField(null=True, blank=True)
    qty = models.PositiveIntegerField(default=1)
    price = models.IntegerField()
    ordered_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50, default=OrderStatus.PENDING, choices=OrderStatus.choices)

    def __str__(self):
        return f"Order Detail - User: {self.user}, Product: {self.product_name}, Status: {self.get_status_display()}"
