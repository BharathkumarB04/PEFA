from django.db import models
from django.contrib.auth.models import User
# Create your models here.
class Expense(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    amount= models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()
    uploaded_bill = models.FileField(upload_to='documents/', blank=True, null=True)

    def __str__(self):
        return f"{self.title}-{self.user.username}"

class MonthlyBudget(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    year = models.IntegerField()
    month = models.IntegerField()

    def _str_(self):
        return f"{self.category} - {self.month}/{self.year}"
class SavingsGoal(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    goal_amount = models.FloatField()
    saved_amount = models.FloatField(default=0)
    remaining_amount = models.FloatField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        self.remaining_amount = self.goal_amount - self.saved_amount
        super().save(*args, **kwargs)

    @property
    def progress(self):
        return (self.saved_amount / self.goal_amount) * 100 if self.goal_amount else 0

    def _str_(self):
        return self.title
        
class UserPreferences(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    currency = models.CharField(max_length=5, default="INR")

    def _str_(self):
        return f"{self.user.username} - {self.currency}"

class UserStock(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    stock_symbol = models.CharField(max_length=10)
    buy_price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.IntegerField()
    buy_date = models.DateField()

    def _str_(self):
        return self.stock_symbol
class SIPInvestment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    sip_name = models.CharField(max_length=255)
    scheme_code = models.CharField(max_length=50, blank=True, null=True)  # Needed for API fetching
    purchase_date = models.DateField()
    invested_amount = models.DecimalField(max_digits=10, decimal_places=2)
    units_bought = models.DecimalField(max_digits=10, decimal_places=4)
    current_nav = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True)
    last_updated = models.DateTimeField(auto_now=True)

    def _str_(self):
        return f"{self.sip_name} - {self.user.username}"

class SIPNAVHistory(models.Model):
    sip = models.ForeignKey(SIPInvestment, on_delete=models.CASCADE, related_name="nav_history")
    date = models.DateField()
    nav = models.DecimalField(max_digits=10, decimal_places=4)

    def _str_(self):
        return f"{self.sip.sip_name} - {self.date} - {self.nav}"

class FAQ(models.Model):
    question = models.CharField(max_length=255)  # Stores the question
    answer = models.TextField()  # Stores the answer

    def _str_(self):
        return self.question

class FinancialProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    income = models.FloatField(default=0)
    savings = models.FloatField(default=0)
    balance = models.FloatField(default=0)
    expenses = models.FloatField(default=0)
    investment = models.FloatField(default=0, blank=True, null=True)
    financial_health_score = models.FloatField(default=100)
    badge = models.CharField(max_length=50, default="No Badge")

    def _str_(self):
        return f"{self.user.username} - {self.financial_health_score} - {self.badge}"