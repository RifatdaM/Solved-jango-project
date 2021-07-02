from django.db import models
from django.contrib.auth.models import User
from django_countries.fields import CountryField
from phonenumber_field.modelfields import PhoneNumberField
from django.utils import timezone

from django.urls import reverse

DIV = [
    ('dhaka', 'Dhaka'),
    ('rajshahi', 'Rajshahi'),
    ('rangpur', 'Rangpur'),
    ('sylhet', 'Sylhet'),
    ('khulna', 'Khulna'),
    ('chittagong', 'Chittagong'),
    ('barishal', 'Barishal'),
    ]
stat = [
    ('pending', 'pending'),
    ('waiting for confirmation', 'waiting for confirmation'),
    ('invalid transaction id', 'invalid transaction id'),
    ('completed', 'completed'),
    ('canceled', 'canceled'),
    ('unconfirmed', 'unconfirmed'),
    ('confirmed', 'confirmed'),
]

stat2 = [
    ('not_verified', 'not_verified'),
    ('verified', 'verified'),
    ('pending', 'pending'),
    ('new', 'new'),
]

state = [
    ('active', 'active'),
    ('inactive', 'inactive'),
]

gateway_from = [
    ('paypal', 'Paypal'),
    ('payoneer', 'Payoneer'),
    ('skrill', 'Skrill'),
    ('neteller', 'Neteller'),
    ('bkash', 'Bkash'),
    ('btcusd', 'BTC USD'),
]

gateway_to = [
    ('paypal', 'Paypal'),
    ('payoneer', 'Payoneer'),
    ('skrill', 'Skrill'),
    ('neteller', 'Neteller'),
    ('bkash', 'Bkash'),
    ('btcusd', 'BTC USD'),
]

msg_status = [
    ('unseen', 'unseen'),
    ('replied', 'replied'),
]

review_msg_status = [
    ('hide', 'hide'),
    ('show', 'show'),
    ('uncensored', 'uncensored'),
]

class BTC_wallet_address(models.Model):
    title = models.CharField(max_length=100)
    belonging_order_id = models.IntegerField()
    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

class We_send(models.Model):
    title = models.CharField(max_length=100)
    unit = models.CharField(max_length=15)
    state = models.CharField(max_length=10, choices=state, default='active')
    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

class We_rcv(models.Model):
    title = models.CharField(max_length=100)
    unit = models.CharField(max_length=15)
    state = models.CharField(max_length=10, choices=state, default='active')
    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

class Actual_cash_flow_total(models.Model):
    title = models.CharField(max_length=100)
    incoming = models.FloatField()
    outgoing = models.FloatField()
    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

class Actual_cash_flow_account_wise(models.Model):
    title = models.CharField(max_length=100)
    gateway = models.CharField(max_length=100)
    account_name = models.CharField(max_length=100)
    incoming = models.FloatField()
    outgoing = models.FloatField()
    belonging_order_id = models.IntegerField()
    time = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

class Profile_info(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    address = models.CharField(max_length=200)
    address2 = models.CharField(max_length=200)
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=100, choices=DIV)
    zip = models.CharField(max_length=20)
    country_code = CountryField()
    phone = PhoneNumberField()
    profile_status = models.CharField(max_length=100, choices=stat2, default='new')

    def __str__(self):
        return f'{self.user.username} Profile'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

class MinMaxFloat(models.FloatField):
    def __init__(self, min_value=None, max_value=None, *args, **kwargs):
        self.min_value, self.max_value = min_value, max_value
        super(MinMaxFloat, self).__init__(*args, **kwargs)

    def formfield(self, **kwargs):
        defaults = {'min_value': self.min_value, 'max_value' : self.max_value}
        defaults.update(kwargs)
        return super(MinMaxFloat, self).formfield(**defaults)

class orders_without_trxID(models.Model):
    title = models.CharField(max_length=100)
    sent_from = models.CharField(max_length =100)
    receive_at = models.CharField(max_length = 100)
    sent_amount = MinMaxFloat(min_value = 0.0, max_value = 100000.0)
    to_be_sent = MinMaxFloat(min_value=0.0, max_value=100000.0)
    send_unit = models.CharField(max_length = 10)
    rcv_unit = models.CharField(max_length=10)
    date_ordered = models.DateTimeField(default=timezone.now)
    admin_receiving_account = models.CharField(default='', max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.title
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
    '''def get_absolute_url(self):
        return reverse('home-blog')#,kwargs={'pk':self.pk})'''

class order_with_trxID(models.Model):
    title = models.CharField(max_length=100)
    belonging_order_id = models.CharField(max_length = 100)
    sent_from = models.CharField(max_length=100)
    receive_at = models.CharField(max_length=100)
    sent_amount = models.FloatField()
    to_be_sent = models.FloatField()
    send_acount = models.CharField(max_length=100)
    trx_id = models.CharField(max_length=100)
    rcv_acount = models.CharField(max_length=200)
    send_unit = models.CharField(max_length=10)
    rcv_unit = models.CharField(max_length=10)
    status = models.CharField(max_length=100, choices=stat, default='pending')
    transaction_amount = models.FloatField()
    date_ordered = models.DateTimeField(default=timezone.now)
    admin_receiving_account = models.CharField(default='', max_length=100)
    admin_sending_account = models.CharField(default='', max_length=100)
    order_processed_by = models.IntegerField(default=0)
    admin_transaction_id = models.CharField(default='', max_length=100)
    admin_rcv_btc_wallet = models.CharField(default='na', max_length=100)
    admin_send_btc_wallet = models.CharField(default='na', max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    def __str__(self):
        return self.title
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

class new_trx_id(models.Model):
    title = models.CharField(max_length=100)
    correct_trx_id = models.CharField(max_length=100)
    belonging_order_id = models.CharField(max_length = 100)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    def __str__(self):
        return self.title
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

class Contact_us(models.Model):
    title = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    email = models.EmailField(max_length=150)
    topic = models.CharField(max_length=150)
    content = models.TextField(max_length=25000)
    state = models.CharField(max_length=100, choices=msg_status, default='unseen')
    date_created = models.DateTimeField(default=timezone.now)
    def __str__(self):
        return self.title
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

class Review_msg(models.Model):
    title = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    msg = models.TextField(max_length=25000)
    length = models.IntegerField()
    rating = models.IntegerField()
    state = models.CharField(max_length=100, choices=review_msg_status, default='hide')
    date_created = models.DateTimeField(default=timezone.now)
    def __str__(self):
        return self.title
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

class reserve_balances_rates(models.Model):
    title = models.CharField(max_length=100, unique=True)
    minim = models.FloatField()
    maxim = models.FloatField()
    reserve_am = models.FloatField()
    unit = models.CharField(max_length=10)
    skrill = models.FloatField()
    neteller = models.FloatField()
    paypal = models.FloatField()
    payoneer = models.FloatField()
    bkash = models.FloatField()
    btcusd = models.FloatField()
    from_com = models.FloatField()
    to_com = models.FloatField()
    def __str__(self):
        return self.title
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

class conversion_rate(models.Model):
    title = models.CharField(max_length=100, unique=True)
    skrill = models.FloatField()
    neteller = models.FloatField()
    paypal = models.FloatField()
    payoneer = models.FloatField()
    btcusd = models.FloatField()
    bkash = models.FloatField()
    def __str__(self):
        return self.title
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

class our_ids(models.Model):
    title = models.CharField(max_length=100)
    address = models.CharField(max_length=100)
    state = models.CharField(max_length=100, choices=state, default='active')
    send_count = models.IntegerField(default=0)
    rcv_count = models.IntegerField(default=0)
    reserve = models.FloatField(default=0.0)
    def __str__(self):
        return self.title
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

class Order_processed_By(models.Model):
    title = models.CharField(max_length=100)
    processed_by = models.ForeignKey(User, on_delete=models.CASCADE)
    made_status = models.CharField(max_length=100, default='na')
    order = models.IntegerField()
    def __str__(self):
        return self.title
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

class File(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    file = models.FileField(upload_to='files/')
    file2 = models.FileField(upload_to='files/')

    def __str__(self):
        return self.user.username + "files"
