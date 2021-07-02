from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django_countries.fields import CountryField
from .models import Profile_info, orders_without_trxID, order_with_trxID, new_trx_id, File, Contact_us, Review_msg,\
    Actual_cash_flow_total, Actual_cash_flow_account_wise, BTC_wallet_address
from phonenumber_field.modelfields import PhoneNumberField
from django import forms
from django.template.defaultfilters import filesizeformat
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from bootstrap_modal_forms.mixins import PopRequestMixin, CreateUpdateAjaxMixin

from django.urls import reverse
'''class PhotoForm(forms.ModelForm):
    class Meta:
        model = Photo
        fields = ('file', )'''
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
]

review_msg_status = [
    ('hide', 'hide'),
    ('show', 'show'),
    ('uncensored', 'uncensored'),
]

stat2 = [
    ('not_verified', 'not_verified'),
    ('verified', 'verified'),
    ('pending', 'pending'),
    ('new', 'new'),
]

class UserRegisterForm(UserCreationForm):
    first_name = forms.CharField(max_length=100)
    last_name = forms.CharField(max_length=100)
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['first_name','last_name','username','email','password1','password2']



class User_address_form(forms.ModelForm):
    '''address = forms.CharField(max_length=200)
    address2 = forms.CharField(max_length=200)
    city = forms.CharField(max_length=50)
    state = forms.CharField(widget=forms.Select(choices=DIV))
    zip = forms.CharField(max_length=20)
    country_code = CountryField()
    phone = PhoneNumberField()'''
    class Meta:
        model = Profile_info
        fields = ['address','address2','city','state','zip', 'country_code', 'phone']



class OrederForm(forms.ModelForm):
    class Meta:
        model = orders_without_trxID
        fields = ['sent_from','receive_at','sent_amount','to_be_sent']

class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact_us
        fields = ['email','topic','content']

class Review_msg_form(PopRequestMixin, CreateUpdateAjaxMixin, forms.ModelForm):
    rating = forms.IntegerField(max_value=5, min_value=0)
    class Meta:
        model = Review_msg
        fields = ['msg', 'rating']

class Review_msg_approval_form(forms.Form):
    state = forms.CharField(label='State', widget=forms.Select(choices=review_msg_status))
    review_id = forms.IntegerField()
    class Meta:
        fields = ['state', 'review_id']

class AddressUpdateFormm(PopRequestMixin, CreateUpdateAjaxMixin, forms.ModelForm):
    class Meta:
        model = Profile_info
        fields = ['address', 'address2','city', 'state', 'zip', 'country_code']

class PhoneUpdateFormm(PopRequestMixin, CreateUpdateAjaxMixin, forms.ModelForm):
    class Meta:
        model = Profile_info
        fields = ['phone']

class ConfirmOrederForm(forms.ModelForm):
    class Meta:
        model = order_with_trxID
        fields = ['belonging_order_id','send_acount', 'trx_id', 'rcv_acount']

class ConfirmOrederForm_btc(forms.ModelForm):
    class Meta:
        model = order_with_trxID
        fields = ['belonging_order_id','rcv_acount']

class Correct_trx_ID(forms.ModelForm):
    class Meta:
        model = new_trx_id
        fields = ['correct_trx_id', 'belonging_order_id']

class UserForm(forms.Form):
    first_name= forms.CharField(max_length=100)
    last_name= forms.CharField(max_length=100)
    email= forms.EmailField()
    age= forms.IntegerField()
    from_where = forms.CharField(label='', widget=forms.Select(choices=DIV))


'''class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField

    class Meta:
        model = User
        fields = ['username','email']'''

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile_info
        fields = ['address','address2','city','state','zip', 'country_code', 'phone']

class ProfileStatusForm(forms.Form):
    profile_status = forms.CharField(label='Status', widget=forms.Select(choices=stat2))
    user_id = forms.IntegerField()
    class Meta:
        fields = ['profile_status', 'user_id']

class RestrictedFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        self.content_types = kwargs.pop('content_types', None)
        self.max_upload_size = kwargs.pop('max_upload_size', None)
        if not self.max_upload_size:
            self.max_upload_size = settings.MAX_UPLOAD_SIZE
        super(RestrictedFileField, self).__init__(*args, **kwargs)

    def clean(self, *args, **kwargs):
        data = super(RestrictedFileField, self).clean(*args, **kwargs)
        try:
            if data.content_type in self.content_types:
                if data.size > self.max_upload_size:
                    raise forms.ValidationError(_('File size must be under %s. Current file size is %s.') % (filesizeformat(self.max_upload_size), filesizeformat(data.size)))
            else:
                raise forms.ValidationError(_('File type (%s) is not supported.') % data.content_type)
        except AttributeError:
            pass

        return data

class RestrictedImageField(forms.ImageField):
    def __init__(self, *args, **kwargs):
        self.max_upload_size = kwargs.pop('max_upload_size', None)
        if not self.max_upload_size:
            self.max_upload_size = settings.MAX_UPLOAD_SIZE
        super(RestrictedImageField, self).__init__(*args, **kwargs)

    def clean(self, *args, **kwargs):
        data = super(RestrictedImageField, self).clean(*args, **kwargs)
        try:
            if data.size > self.max_upload_size:
                raise forms.ValidationError(_('File size must be under %s. Current file size is %s.') % (filesizeformat(self.max_upload_size), filesizeformat(data.size)))
        except AttributeError:
            pass

        return data



class FileForm(forms.ModelForm):
    file = RestrictedFileField(content_types=['image/jpeg', 'application/pdf', 'image/jpg'])
    file2 = RestrictedFileField(content_types=['image/jpeg', 'application/pdf', 'image/jpg'])
    class Meta:
        model = File
        fields = ['file', 'file2']


class ProcessFrom1(forms.Form):
    status = forms.CharField(widget=forms.Select(choices=stat))
    admin_received = forms.FloatField()
    admin_sends = forms.FloatField()
    admin_sending_acc = forms.CharField(max_length=100)
    admin_transaction_id = forms.CharField(max_length=100)
    class Meta:
        fields = ['status', 'admin_received', 'admin_sends', 'admin_sending_acc', 'admin_transaction_id']

class ProcessFrom2(forms.Form):
    total_reserve_amount = forms.FloatField()

    class Meta:
        fields = ['total_reserve_amount']

class ProcessFrom3(forms.Form):
    account_reserve_amount = forms.FloatField()

    class Meta:
        fields = ['account_reserve_amount']

class WalletAddressForm(forms.ModelForm):
    class Meta:
        model = BTC_wallet_address
        fields = ['title']

class StatusForm(forms.Form):
    status = forms.CharField(widget=forms.Select(choices=stat))
    class Meta:
        fields = ['status']

class Admin_sending_btc_wallet(forms.Form):
    wallet = forms.CharField(max_length=200)
    class Meta:
        fields = ['wallet']

class ReplyFrom(forms.Form):
    msg = forms.CharField(widget=forms.Textarea)
    class Meta:
        fields = ['msg']