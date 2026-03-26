from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=100)
    
    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=200)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    weight_in_stock = models.DecimalField(max_digits=10, decimal_places=2, help_text="Current weight in KGs")
    buying_price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Price bought per KG")
    selling_price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Price sold per KG")
    min_stock_level = models.DecimalField(max_digits=10, decimal_places=2, default=10.00, help_text="Alert when stock hits this weight")

    def __str__(self):
        return f"{self.name} - {self.weight_in_stock}kg"

    @property
    def is_low_stock(self):
        return self.weight_in_stock <= self.min_stock_level


class Sale(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity_sold = models.DecimalField(max_digits=10, decimal_places=2, help_text="Weight sold in KGs")
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # Business Logic: Automatically reduce stock when a sale is made!
        self.product.weight_in_stock -= self.quantity_sold
        self.product.save()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Sale: {self.product.name} - {self.quantity_sold}kg"