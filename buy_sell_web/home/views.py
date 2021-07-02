from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseServerError
from django.contrib import messages
from .forms import OrederForm, UserRegisterForm, User_address_form,\
    ConfirmOrederForm, Correct_trx_ID, FileForm, ContactForm, Review_msg_form, \
    AddressUpdateFormm, PhoneUpdateFormm, ConfirmOrederForm_btc, ProcessFrom1,\
    ProcessFrom2, WalletAddressForm, StatusForm, ProcessFrom3, ReplyFrom,\
    Review_msg_approval_form, ProfileStatusForm, Admin_sending_btc_wallet
from django.http import HttpResponse
from django.contrib.auth import login, authenticate
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_text
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from .tokens import account_activation_token
from django.contrib.auth.models import User
from django.core.mail import EmailMessage
from django.contrib.auth.decorators import login_required
from .models import Profile_info, orders_without_trxID, order_with_trxID, new_trx_id,\
    reserve_balances_rates, File, our_ids, Review_msg, conversion_rate,\
    Actual_cash_flow_total, Actual_cash_flow_account_wise, BTC_wallet_address,\
    Order_processed_By, Contact_us, We_rcv, We_send
import datetime
from django.http import JsonResponse
from django.db.models import Q
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from bootstrap_modal_forms.mixins import PassRequestMixin
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
from django.contrib.auth.views import PasswordChangeView
from django.urls import reverse
from django.db.models import Avg, Sum, Min
from django.contrib import messages
from django.core.paginator import Paginator
from bootstrap_modal_forms.generic import (BSModalCreateView,
                                           BSModalUpdateView,
                                           BSModalReadView,
                                           BSModalDeleteView)

from blockchain.v2.receive import receive, balance_updates
from blockchain.exchangerates import to_btc
import json
from meta.views import Meta

from django.http import HttpResponseNotFound


def error_404(request, exception):
        data = {}
        return render(request,'home/404.html', data)

def test(request):
    return HttpResponseNotFound("404 Not Found")

meta = Meta(
    title="Exontime|Easily exchange your money",
    description='The best site for exchanging your emoney around the world in bangladesh. ',
    keywords=['Exontime', 'exontime', 'easy exchange', 'money exchange', 'money transfaer', 'money exchnage in bangladesh',
              'dollar buy sell', 'skrill dollar buy', 'neteller buy sell', 'paypal to skrill', 'btc to bkash', ' paypal to bkash',
              'webmoney dollar buy'],
    extra_props = {
        'viewport': 'width=device-width, initial-scale=1.0, minimum-scale=1.0'
    },
    extra_custom_props=[
        ('http-equiv', 'X-UA-Compatible', 'IE=edge; charset=UTF-8'),
    ]
)

def google_ver(request):
    return render(request, 'home/google7b7a092bf0942f76.html')

def paypal_payment(request):
    return render(request, 'home/paypal_payment.html',{'title':'payment'})

def terms_conditions(request):
    return render(request, 'home/terms_cond.html',{'title':'Policies'})

def priv_poli(request):
    return render(request, 'home/priv_poli.html',{'title':'Policies'})

def aml_poli(request):
    return render(request, 'home/AML_poli.html',{'title':'Policies'})

def refund_poli(request):
    return render(request, 'home/refund_policy.html',{'title':'Policies'})

def about_us(request):
    return render(request, 'home/about_us.html',{'title':'About Us'})

def help_page(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            hlp = form.save(commit=False)
            hlp.user = request.user
            hlp.title = request.user.username + '@' + str(datetime.datetime.now())
            hlp.save()
            messages.success(request, 'Form submission successful')
            return redirect('help')
    else:
        form = ContactForm()
    context = {
        'form': form,
    }
    return render(request, 'home/help.html', context)

class CompletedOrder(ListView, LoginRequiredMixin):
    model = order_with_trxID
    template_name = 'home/completed_orders.html'
    context_object_name = 'orders'
    ordering = ['-belonging_order_id']
    paginate_by = 15
    def get_queryset(self):
        #user = get_object_or_404(User, username=self.kwargs.get('username'))
        return order_with_trxID.objects.filter(user = self.request.user).filter(Q(status='completed') | Q(status='canceled')).order_by('-belonging_order_id')

class PendingOrder(ListView, LoginRequiredMixin):
    model = order_with_trxID
    template_name = 'home/pending_transactions.html'
    context_object_name = 'orders'
    ordering = ['-belonging_order_id']
    paginate_by = 15
    def get_queryset(self):
        #user = get_object_or_404(User, username=self.kwargs.get('username'))
        return order_with_trxID.objects.filter(user = self.request.user).filter(Q(status='pending') | Q(status='waiting for confirmation')).order_by('-belonging_order_id')

class CompletedOrderDetails(LoginRequiredMixin, BSModalReadView):
    model = order_with_trxID
    context_object_name = 'order'
    template_name = 'home/order_details.html'


def home(request):
    rates = reserve_balances_rates.objects.all()
    can_review = False
    if request.user.is_authenticated:
        order_count_of_user = order_with_trxID.objects.filter(user = request.user).filter(status = 'completed')
        if len(order_count_of_user) > 0:
            can_review = True
    sends = We_rcv.objects.filter(state = 'active')
    rcvs = We_send.objects.filter(state = 'active')
    send_initial = sends[0]
    rcv_initial = rcvs[len(rcvs)-1]
    conversions = conversion_rate.objects.all()
    orders = order_with_trxID.objects.all().order_by('-id')
    total_rating = Review_msg.objects.filter(state = 'show').aggregate(Avg('rating'))
    date_from = datetime.datetime.now() - datetime.timedelta(hours=24)
    transaction_today = order_with_trxID.objects.filter(date_ordered__gte=date_from).aggregate(Sum('transaction_amount'))
    order_count = len(orders)
    if (len(orders) > 10):
        orders = orders[:10]
    rates_1 = rates[:3]
    rates_2 = rates[3:]
    review_count = len(Review_msg.objects.all().values())
    reviews = Review_msg.objects.filter(state = 'show').filter(length__lte = 200).order_by('-id')
    if (len(reviews) > 10):
        reviews = reviews[:10]
    rev_ord_count = {'review_count': review_count, 'order_count': order_count}
    if request.method == 'POST':
        form = OrederForm(request.POST)
        if form.is_valid():
            data = request.POST.copy()
            reserve_instance = reserve_balances_rates.objects.get(title=data.get('receive_at'))
            if(float(data.get('to_be_sent'))<reserve_instance.reserve_am):
                order = form.save(commit=False)
                order.user = request.user
                order.title = request.user.username + '@' + str(datetime.datetime.now())
                unit1 = reserve_balances_rates.objects.get(title=order.sent_from)
                order.send_unit = unit1.unit
                unit2 = reserve_balances_rates.objects.get(title=order.receive_at)
                order.rcv_unit = unit2.unit
                #unit2.reserve_am = unit2.reserve_am - order.to_be_sent
                #unit2.save()
                order.save()
                orderId = order.id
                # username = form.cleaned_data.get('username')
                # messages.success(request, f'Order received!')
                return redirect('upload_trxid', order_id = orderId)
            else:
                messages.success(request, 'Sorry! We are unable to process your order right now.')
                return redirect('home')
    else:
        form = OrederForm()
    context = {
        'rates': rates,
        'rates_1': rates_1,
        'rates_2': rates_2,
        'reviews': reviews,
        'conversions': conversions,
        'orders': orders,
        'total_rating': total_rating,
        'transaction_today': transaction_today,
        'form': form,
        'rev_ord_count': rev_ord_count,
        'rcvs': rcvs,
        'sends': sends,
        'send_initial': send_initial,
        'rcv_initial': rcv_initial,
        'meta': meta,
        'can_review': can_review
    }
    return render(request, 'home/welcome_page2.html', context)

'''def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}! , you can now login')
            return redirect('login')
    else:
        form = UserRegisterForm()

    return render(request, 'home/register.html',{'form':form})'''

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            current_site = get_current_site(request)
            mail_subject = 'Activate your account.'
            message = render_to_string('home/acc_active_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user),
            })
            to_email = form.cleaned_data.get('email')
            email = EmailMessage(
                mail_subject, message, to=[to_email]
            )
            email.send()
            return render(request, 'home/email_verify.html')
            #return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'home/register2.html', {'form': form})


def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        # return redirect('home')
        return render(request, 'home/account_verified.html')
    else:
        return render(request, 'home/verification_failed.html')

class ReviewMsgView(LoginRequiredMixin, PassRequestMixin, SuccessMessageMixin, CreateView):
    form_class = Review_msg_form
    template_name = 'home/review_msg.html'
    success_message = 'Success: Thanks for writing a review.'
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.title = self.request.user.username + '@' + str(datetime.datetime.now())
        form.instance.length = len(form.cleaned_data.get("msg", ""))
        form.instance.state = 'hide'
        return super().form_valid(form)
        #return HttpResponse(render_to_string('myapp/item_edit_form_success.html', {'item': item}))

class CustomPasswordChangeView(LoginRequiredMixin, PasswordChangeView):
    template_name = 'home/change_password.html'
    def get_success_url(self):
        success_url = reverse_lazy('password_change_done')
        return success_url

login_after_password_change = login_required(CustomPasswordChangeView.as_view())

class AddressUpdateView(LoginRequiredMixin, PassRequestMixin, SuccessMessageMixin, CreateView):
    form_class = AddressUpdateFormm
    template_name = 'home/address_update.html'
    success_message = 'Success: Thanks for providing information.'
    success_url = reverse_lazy('settings')

    def get_success_url(self):
        return reverse_lazy('settings')

    '''def form_valid(self, form):
        user = self.request.user.id
        print(user)
        self.object = form.save(commit=False)
        self.object.user_id = self.request.user.id
        self.object.profile_status = 'not_verified'
        self.object.save()
        #return HttpResponseRedirect(self.object.get_absolute_url())
        return super().form_valid(form)
        #return HttpResponse(render_to_string('myapp/item_edit_form_success.html', {'item': item}))'''

    def form_valid(self, form):
        user = self.request.user
        instance, _ = Profile_info.objects.get_or_create(user=user)
        instance.address = form.cleaned_data.get("address", "")
        instance.address2 = form.cleaned_data.get("address2", "")
        instance.city = form.cleaned_data.get("city", "")
        instance.state = form.cleaned_data.get("state", "")
        instance.zip = form.cleaned_data.get("zip", "")
        instance.country_code = form.cleaned_data.get("country_code", "")
        instance.profile_status = 'not_verified'
        instance.save()
        return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        new_context_entry = Profile_info.objects.get(user = self.request.user)
        context["profile"] = new_context_entry
        return context

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(AddressUpdateView, self).dispatch(request, *args, **kwargs)


class PhoneUpdateView(LoginRequiredMixin, PassRequestMixin, SuccessMessageMixin, CreateView):
    form_class = PhoneUpdateFormm
    template_name = 'home/phone_update.html'
    success_message = 'Success: Thanks for providing information.'
    success_url = reverse_lazy('settings')

    def get_success_url(self):
        return reverse_lazy('settings')

    def form_valid(self, form):
        user = self.request.user
        instance, _ = Profile_info.objects.get_or_create(user=user)
        instance.phone = form.cleaned_data.get("phone", "")
        instance.profile_status = 'not_verified'
        instance.save()
        return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        new_context_entry = Profile_info.objects.get(user = self.request.user)
        context["profile"] = new_context_entry
        return context

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(PhoneUpdateView, self).dispatch(request, *args, **kwargs)


@login_required
def address(request):
    if request.method == 'POST':
        form = User_address_form(request.POST, instance=request.user.profile_info)
        if form.is_valid():
            form.save()
            idd = request.user.id
            corr = Profile_info.objects.get(user_id=idd)
            corr.profile_status = 'not_verified'
            corr.save()
            #username = form.cleaned_data.get('username')
            #messages.success(request, f'address saved! , you can now login')
            return redirect('dashboard')
    else:
        form = User_address_form()
    return render(request, 'home/address_taker.html', {'form': form})

def update_page_dashboard(request):
    if request.method == "GET" and request.is_ajax():
        from_val = request.GET.get('from', None)
        to_val = request.GET.get('to', None)
        if from_val and to_val:
            data = reserve_balances_rates.objects.filter(Q(title=from_val) | Q(title=to_val)).values()
        else:
            data = reserve_balances_rates.objects.all().values()
        data2 = conversion_rate.objects.all().values()
        res = list(data)
        res2 = list(data2)
        #print(res)
        return JsonResponse({"reserves": res, "convert": res2}, status=200)
    return JsonResponse({"success": False}, status=400)

def admin_search_ajax(request):
    if request.method == "GET" and request.is_ajax():
        order_id = request.GET.get('order_id', None)
        data1 = order_with_trxID.objects.filter(belonging_order_id = order_id)
        data2 = orders_without_trxID.objects.filter(id=order_id)
        if data1.exists():
            dt = order_with_trxID.objects.filter(belonging_order_id=order_id).values()
        elif data2.exists():
            dt = orders_without_trxID.objects.filter(id=order_id).values()
        else:
            dt = [{"id": "not_available"}]
        res = list(dt)
        return JsonResponse({"search_result": res}, status=200)
    return JsonResponse({"success": False}, status=400)


def search_ajax(request):
    if request.method == "GET" and request.is_ajax():
        order_id = request.GET.get('order_id', None)
        data1 = order_with_trxID.objects.filter(user = request.user).filter(belonging_order_id = order_id)
        data2 = orders_without_trxID.objects.filter(user = request.user).filter(id=order_id)
        if data1.exists():
            dt = order_with_trxID.objects.filter(belonging_order_id=order_id).values()
        elif data2.exists():
            dt = orders_without_trxID.objects.filter(id=order_id).values()
        else:
            dt = [{"id": "not_available"}]
        res = list(dt)
        return JsonResponse({"search_result": res}, status=200)
    return JsonResponse({"success": False}, status=400)

def search_ajax_completed_order(request):
    if request.method == "GET" and request.is_ajax():
        order_id = request.GET.get('order_id', None)
        data1 = order_with_trxID.objects.filter(user = request.user).filter(belonging_order_id = order_id).filter(Q(status='completed') | Q(status='canceled'))
        if data1.exists():
            dt = order_with_trxID.objects.filter(user = request.user).filter(belonging_order_id=order_id).filter(Q(status='completed') | Q(status='canceled')).values()
        else:
            dt = [{"id": "not_available"}]
        res = list(dt)
        return JsonResponse({"search_result": res}, status=200)
    return JsonResponse({"success": False}, status=400)

def search_ajax_pending_order(request):
    if request.method == "GET" and request.is_ajax():
        order_id = request.GET.get('order_id', None)
        data1 = order_with_trxID.objects.filter(user = request.user).filter(belonging_order_id = order_id).filter(status = 'pending')
        if data1.exists():
            dt = order_with_trxID.objects.filter(user = request.user).filter(belonging_order_id=order_id).filter(status = 'pending').values()
        else:
            dt = [{"id": "not_available"}]
        res = list(dt)
        return JsonResponse({"search_result": res}, status=200)
    return JsonResponse({"success": False}, status=400)

@login_required
def exchange_rate(request):
    reserves = reserve_balances_rates.objects.all()
    context = {
        'reserves': reserves,
    }
    return render(request, 'home/exchange-rates.html', context)

@login_required
def track_order(request):
    user = request.user.id
    unconfirmed_orders = orders_without_trxID.objects.filter(user_id=user)
    confirmed_oreders = order_with_trxID.objects.filter(user_id=user)
    context = {
        'confirmed_oreders': confirmed_oreders,
        'unconfirmed_orders': unconfirmed_orders
    }
    return render(request, 'home/track_order.html', context)

@login_required
def track_your_order(request):
    return render(request, 'home/track_your_order.html')

@login_required
def settings(request):
    user = request.user.id
    user_info = Profile_info.objects.get(user_id=user)
    context = {
        'user_info': user_info,
    }
    return render(request, 'home/edit_profile.html', context)

@login_required
def order_history(request):
    user = request.user.id
    orders = order_with_trxID.objects.filter(user = user).filter(Q(status='completed') | Q(status='canceled')).order_by('-belonging_order_id')
    context = {
        'orders': orders,
    }
    return render(request, 'home/order_history.html', context)

@login_required
def pending_order(request):
    user = request.user.id
    orders = order_with_trxID.objects.filter(user = user).filter(Q(status='pending') | Q(status='invalid transaction id') | Q(status = 'waiting for confirmation')).order_by('-belonging_order_id')
    context = {
        'orders': orders,
    }
    return render(request, 'home/pending_order.html', context)

@login_required
def contact_us(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            help = form.save(commit=False)
            help.user = request.user
            help.title = request.user.username + '@' + str(datetime.datetime.now())
            help.save()
            messages.success(request, 'Form submission successful')
            return redirect('contact_us')
    else:
        form = ContactForm()


    context = {
        'form': form,
    }
    return render(request, 'home/contact_us.html', context)

@login_required
def up_trx_id(request, order_id):
    user = request.user
    order = orders_without_trxID.objects.filter(user = user).get(id = order_id)
    if order.sent_from != 'btcusd':
        if(order.admin_receiving_account == ''):
            out = our_ids.objects.filter(title = order.sent_from).aggregate(Min('rcv_count'))
            av_ids = our_ids.objects.filter(title = order.sent_from).filter(rcv_count=out['rcv_count__min'])[0]
            order.admin_receiving_account = av_ids.address;
            av_ids.rcv_count = av_ids.rcv_count + 1
            av_ids.save()
            order.save()
        else:
            av_ids = our_ids.objects.filter(title = order.sent_from).get(address = order.admin_receiving_account)

    if request.method == 'POST':
        form2 = ConfirmOrederForm(request.POST)
        form4 = ConfirmOrederForm_btc(request.POST)
        if form2.is_valid() and 'trx_id' in request.POST:
            confirmorder = form2.save(commit=False)
            confirmorder.user = request.user
            confirmorder.title = request.user.username + '@' + str(datetime.datetime.now())
            bOrderID = confirmorder.belonging_order_id
            instance = orders_without_trxID.objects.get(id=bOrderID)
            inst2 = conversion_rate.objects.all().values()
            inst2 = list(inst2)
            confirmorder.sent_from = instance.sent_from
            confirmorder.receive_at = instance.receive_at
            confirmorder.send_unit = instance.send_unit
            confirmorder.rcv_unit = instance.rcv_unit
            confirmorder.sent_amount = instance.sent_amount
            confirmorder.to_be_sent = instance.to_be_sent
            our_accs = our_ids.objects.filter(title=order.sent_from).get(address=order.admin_receiving_account)
            confirmorder.admin_receiving_account = av_ids.address
            if (confirmorder.send_unit == 'BDT'):
                if confirmorder.rcv_unit == 'BDT':
                    confirmorder.transaction_amount = confirmorder.sent_amount / 82
                else:
                    confirmorder.transaction_amount = confirmorder.sent_amount / inst2[0][confirmorder.receive_at]
            else:
                confirmorder.transaction_amount = confirmorder.sent_amount

            if confirmorder.sent_from == 'btcusd':
                confirmorder.trx_id = 'Not required'
                confirmorder.send_acount = 'Not required'
                confirmorder.status = 'unconfirmed'
            confirmorder.save()
            reserve_update = reserve_balances_rates.objects.get(title = confirmorder.sent_from)
            reserve_update.reserve_am = reserve_update.reserve_am + confirmorder.sent_amount
            reserve_update.save()
            reserve_instance = reserve_balances_rates.objects.get(title = confirmorder.receive_at)
            reserve_instance.reserve_am = reserve_instance.reserve_am - confirmorder.to_be_sent
            reserve_instance.save()
            our_accs.reserve = our_accs.reserve + confirmorder.sent_amount
            our_accs.save()
            instance.delete()
            current_site = get_current_site(request)
            mail_subject = 'Order confirmation.'
            message = render_to_string('home/order_confirmation_email.html', {
                'user': user,
                'domain': current_site.domain,
                'order_id': confirmorder.belonging_order_id,
                'sent_from': confirmorder.sent_from,
                'sent_amount': confirmorder.sent_amount,
                'receive_at': confirmorder.receive_at,
                'receive_amount': confirmorder.to_be_sent,
                'sent_unit': confirmorder.send_unit,
                'receive_unit': confirmorder.rcv_unit,
                'send_account': confirmorder.send_acount,
                'receive_acount': confirmorder.rcv_acount,
                'date_ordered': datetime.datetime.now(),
                'trx_id': confirmorder.trx_id,
            })
            to_email = request.user.email
            email = EmailMessage(
                mail_subject, message, to=[to_email]
            )
            email.send()
            # messages.success(request, f'Transaction ID uploaded')
            return redirect('dashboard')
        if form4.is_valid() and 'trx_id' not in request.POST:
            confirmorder = form4.save(commit=False)
            confirmorder.user = request.user
            confirmorder.title = request.user.username + '@' + str(datetime.datetime.now())
            bOrderID = confirmorder.belonging_order_id
            instance = orders_without_trxID.objects.get(id=bOrderID)
            inst2 = conversion_rate.objects.all().values()
            inst2 = list(inst2)
            confirmorder.sent_from = instance.sent_from
            confirmorder.receive_at = instance.receive_at
            confirmorder.send_unit = instance.send_unit
            confirmorder.rcv_unit = instance.rcv_unit
            confirmorder.sent_amount = instance.sent_amount
            confirmorder.to_be_sent = instance.to_be_sent
            if (confirmorder.send_unit == 'BDT'):
                if confirmorder.rcv_unit == 'BDT':
                    confirmorder.transaction_amount = confirmorder.sent_amount / 82
                else:
                    confirmorder.transaction_amount = confirmorder.sent_amount / inst2[0][confirmorder.receive_at]
            else:
                confirmorder.transaction_amount = confirmorder.sent_amount

            if confirmorder.sent_from == 'btcusd':
                confirmorder.trx_id = 'Not required'
                confirmorder.send_acount = 'Not required'
                confirmorder.status = 'unconfirmed'
            confirmorder.save()
            reserve_update = reserve_balances_rates.objects.get(title=confirmorder.sent_from)
            reserve_update.reserve_am = reserve_update.reserve_am + confirmorder.sent_amount
            reserve_update.save()
            reserve_instance = reserve_balances_rates.objects.get(title=confirmorder.receive_at)
            reserve_instance.reserve_am = reserve_instance.reserve_am - confirmorder.to_be_sent
            reserve_instance.save()
            instance.delete()
            current_site = get_current_site(request)
            mail_subject = 'Order confirmation.'
            message = render_to_string('home/order_confirmation_email.html', {
                'user': user,
                'domain': current_site.domain,
                'order_id': confirmorder.belonging_order_id,
                'sent_from': confirmorder.sent_from,
                'sent_amount': confirmorder.sent_amount,
                'receive_at': confirmorder.receive_at,
                'receive_amount': confirmorder.to_be_sent,
                'sent_unit': confirmorder.send_unit,
                'receive_unit': confirmorder.rcv_unit,
                'send_account': confirmorder.send_acount,
                'receive_acount': confirmorder.rcv_acount,
                'date_ordered': datetime.datetime.now(),
                'trx_id': confirmorder.trx_id,
            })
            to_email = request.user.email
            email = EmailMessage(
                mail_subject, message, to=[to_email]
            )
            email.send()
            # messages.success(request, f'Transaction ID uploaded')
            return redirect('gen_btc_wallet', order_id = order_id)
    else:
        form2 = ConfirmOrederForm()
        form4 = ConfirmOrederForm_btc()
    if order.sent_from != 'btcusd':
        context = {
            'order': order,
            'form2': form2,
            'av_ids': av_ids,
            'form4': form4,
        }
    else:
        context = {
            'order': order,
            'form2': form2,
            'form4': form4,
        }
    return render(request, 'home/upload_transaction_id.html', context)

@login_required
def btc_payment_after(request, order_id):
    user = request.user
    order = order_with_trxID.objects.filter(user=user).get(belonging_order_id=order_id)
    context = {
        'order': order,
    }
    return render(request, 'home/btc_payment_status.html', context)

@login_required
def gen_btc_wallet(request, order_id):
    user = request.user
    order = order_with_trxID.objects.filter(user=user).filter(status = 'unconfirmed').get(belonging_order_id=order_id)
    callback_url = 'https://www.exontime.com/btc_order_status/'+str(user.id)+'/'+str(order_id)+'/'
    with open('/etc/config.json') as config_file:
        config = json.load(config_file)
    price_in_btc = to_btc('USD', order.sent_amount)
    if not order.admin_receiving_account:
        out = our_ids.objects.filter(title=order.sent_from).aggregate(Min('rcv_count'))
        av_ids = our_ids.objects.filter(title=order.sent_from).filter(rcv_count=out['rcv_count__min'])[0]
        av_ids.rcv_count = av_ids.rcv_count + 1
        av_ids.reserve = av_ids.reserve + order.sent_amount
        av_ids.save()
        if av_ids.address == 'imran_wallet':
            xPub = 'BLOCKCHAIN_X_PUB_1'
        elif av_ids.address == 'nahid_wallet':
            xPub = 'BLOCKCHAIN_X_PUB_2'
        api_key = config['BLOCKCHAIN_API_KEY']
        x_pub = config[xPub]
        recv = receive(x_pub, callback_url, api_key)
        order.admin_receiving_account = av_ids.address
        order.admin_rcv_btc_wallet = recv.address
        order.save()
    context = {
        'order': order,
        'price_in_btc': price_in_btc,
    }
    return render(request, 'home/gen_btc_wallet.html', context)

def btc_payment_status(request, user_id, order_id):
    user = User.objects.get(id = user_id)
    order = order_with_trxID.objects.filter(user=user).filter(status = 'unconfirmed').get(belonging_order_id=order_id)
    order.status = 'waiting for confirmation'
    order.save()
    callback_url = 'https://www.exontime.com/btc_order_confirmation/' + str(user.id) + '/' + str(order_id) + '/'
    with open('/etc/config.json') as config_file:
        config = json.load(config_file)
    api_key = config['BLOCKCHAIN_API_KEY']
    address = order.admin_rcv_btc_wallet
    onNotif = 'DELETE'
    confs = 1
    op = 'RECEIVE'
    balance_confirmation = balance_updates(address, callback_url, api_key, onNotif, op, confs)

    #return render(request, 'home/btc_payment_status.html', context)
    return JsonResponse({"success": balance_confirmation}, status=200)

def btc_payment_confirmation(request, user_id, order_id):
    user = User.objects.get(id = user_id)
    order = order_with_trxID.objects.filter(user=user).filter(status = 'waiting for confirmation').get(belonging_order_id=order_id)
    order.status = 'confirmed'
    order.save()
    #return render(request, 'home/btc_paymenstatust_status.html', context)
    return JsonResponse({"success": True}, status=200)


@login_required
def correct_trx_id(request, order_id):
    user = request.user
    order = order_with_trxID.objects.filter(user = user).filter(status = 'invalid transaction id').get(belonging_order_id = order_id)
    if request.method == 'POST':
        form3 = Correct_trx_ID(request.POST)
        if form3.is_valid() and 'correct_trx_id' in request.POST:
            new_id_rcv = form3.save(commit=False)
            new_id_rcv.user = request.user
            new_id_rcv.title = request.user.username + '@' + str(datetime.datetime.now())
            new_id_rcv.save()
            new_id = new_id_rcv.id
            t_id = new_id_rcv.correct_trx_id
            id1 = new_id_rcv.belonging_order_id
            correction = order_with_trxID.objects.get(id=id1)
            correction.trx_id = t_id
            correction.status = 'pending'
            correction.save()
            inst = new_trx_id.objects.get(id=new_id)
            inst.delete()
            return redirect('dashboard')
    else:
        form3 = Correct_trx_ID()
    context = {
        'order': order,
        'form3': form3,
    }
    return render(request, 'home/correct_transaction_id.html', context)

@login_required
def unconfirmed_order(request):
    user = request.user.id
    orders = orders_without_trxID.objects.filter(user=user)
    invalid_trx_id = order_with_trxID.objects.filter(user=user).filter(status='invalid transaction id')
    unconfirmed_orders = order_with_trxID.objects.filter(user=user).filter(status='unconfirmed')
    context = {
        'orders': orders,
        'invalid_trx_id': invalid_trx_id,
        'unconfirmed_orders': unconfirmed_orders,
    }
    return render(request, 'home/unconfirmed_order.html', context)

@login_required
def profile(request):
    user = request.user.id
    #reserves = reserve_balances_rates.objects.all()
    model = Profile_info.objects.get(user_id=user)
    
    #orders = orders_without_trxID.objects.filter(user = user)
    #av_ids = our_ids.objects.all()
    #invalid_trx_id = order_with_trxID.objects.filter(user = user).filter(status = 'invalid transaction id')
    #complete_order = order_with_trxID.objects.filter(user=user).filter(status='completed').order_by('-belonging_order_id')
    #reviews  = Review_msg.objects.filter(user_id = user)
    #if(len(complete_order) > 3):
    #    complete_order = complete_order[:3]
    #print(orders.id)
    #model = request.user.profile_info
    '''if request.method == 'POST':
        form = OrederForm(request.POST)
        form2 = ConfirmOrederForm(request.POST)
        form3 = Correct_trx_ID(request.POST)
        form4 = ConfirmOrederForm_btc(request.POST)
        #print(request.POST)
        if form.is_valid() and 'rcv_acount' not in request.POST and 'correct_trx_id' not in request.POST:
            order = form.save(commit=False)
            order.user = request.user
            order.title = request.user.username + '@' + str(datetime.datetime.now())
            unit1 = reserve_balances_rates.objects.get(title = order.sent_from)
            order.send_unit = unit1.unit
            unit2 = reserve_balances_rates.objects.get(title=order.receive_at)
            order.rcv_unit = unit2.unit
            order.save()
            # username = form.cleaned_data.get('username')
            #messages.success(request, f'Order received!')
            return redirect('dashboard')
        if form2.is_valid() and 'rcv_acount' in request.POST and 'correct_trx_id' not in request.POST:
            confirmorder = form2.save(commit=False)
            confirmorder.user = request.user
            confirmorder.title = request.user.username + '@' + str(datetime.datetime.now())
            bOrderID = confirmorder.belonging_order_id
            instance = orders_without_trxID.objects.get(id=bOrderID)
            inst2 = conversion_rate.objects.all().values()
            inst2 = list(inst2)
            confirmorder.sent_from = instance.sent_from
            confirmorder.receive_at = instance.receive_at
            confirmorder.send_unit = instance.send_unit
            confirmorder.rcv_unit = instance.rcv_unit
            confirmorder.sent_amount = instance.sent_amount
            confirmorder.to_be_sent = instance.to_be_sent
            if(confirmorder.sent_from == 'bkash'):
                confirmorder.transaction_amount = confirmorder.sent_amount/inst2[0][confirmorder.receive_at]
            else:
                confirmorder.transaction_amount = confirmorder.sent_amount

            if confirmorder.sent_from == 'btcusd':
                confirmorder.trx_id = 'Not required'
                confirmorder.send_acount = 'Not required'
            confirmorder.save()
            instance.delete()
            current_site = get_current_site(request)
            mail_subject = 'Order confirmation.'
            message = render_to_string('home/order_confirmation_email.html', {
                'user': user,
                'domain': current_site.domain,
                'order_id': confirmorder.belonging_order_id,
                'sent_from': confirmorder.sent_from,
                'sent_amount': confirmorder.sent_amount,
                'receive_at': confirmorder.receive_at,
                'receive_amount': confirmorder.to_be_sent,
                'sent_unit': confirmorder.send_unit,
                'receive_unit': confirmorder.rcv_unit,
                'send_account': confirmorder.send_acount,
                'receive_acount': confirmorder.rcv_acount,
                'date_ordered': datetime.datetime.now(),
                'trx_id': confirmorder.trx_id,
            })
            to_email = request.user.email
            email = EmailMessage(
                mail_subject, message, to=[to_email]
            )
            email.send()
            #messages.success(request, f'Transaction ID uploaded')
            return redirect('home')

        if form4.is_valid() and 'rcv_acount' in request.POST and 'correct_trx_id' not in request.POST:
            confirmorder = form4.save(commit=False)
            confirmorder.user = request.user
            confirmorder.title = request.user.username + '@' + str(datetime.datetime.now())
            bOrderID = confirmorder.belonging_order_id
            instance = orders_without_trxID.objects.get(id=bOrderID)
            inst2 = conversion_rate.objects.all().values()
            inst2 = list(inst2)
            confirmorder.sent_from = instance.sent_from
            confirmorder.receive_at = instance.receive_at
            confirmorder.send_unit = instance.send_unit
            confirmorder.rcv_unit = instance.rcv_unit
            confirmorder.sent_amount = instance.sent_amount
            confirmorder.to_be_sent = instance.to_be_sent
            if(confirmorder.sent_from == 'bkash'):
                confirmorder.transaction_amount = confirmorder.sent_amount/inst2[0][confirmorder.receive_at]
            else:
                confirmorder.transaction_amount = confirmorder.sent_amount

            if confirmorder.sent_from == 'btcusd':
                confirmorder.trx_id = 'Not required'
                confirmorder.send_acount = 'Not required'
            confirmorder.save()
            instance.delete()
            current_site = get_current_site(request)
            mail_subject = 'Order confirmation.'
            message = render_to_string('home/order_confirmation_email.html', {
                'user': user,
                'domain': current_site.domain,
                'order_id': confirmorder.belonging_order_id,
                'sent_from': confirmorder.sent_from,
                'sent_amount': confirmorder.sent_amount,
                'receive_at': confirmorder.receive_at,
                'receive_amount': confirmorder.to_be_sent,
                'sent_unit': confirmorder.send_unit,
                'receive_unit': confirmorder.rcv_unit,
                'send_account': confirmorder.send_acount,
                'receive_acount': confirmorder.rcv_acount,
                'date_ordered': datetime.datetime.now(),
                'trx_id': confirmorder.trx_id,
            })
            to_email = request.user.email
            email = EmailMessage(
                mail_subject, message, to=[to_email]
            )
            email.send()
            #messages.success(request, f'Transaction ID uploaded')
            return redirect('home')

        if form3.is_valid() and 'correct_trx_id' in request.POST:
            new_id_rcv = form3.save(commit=False)
            new_id_rcv.user = request.user
            new_id_rcv.title = request.user.username + '@' + str(datetime.datetime.now())
            new_id_rcv.save()
            new_id = new_id_rcv.id
            t_id = new_id_rcv.correct_trx_id
            id1 = new_id_rcv.belonging_order_id
            correction = order_with_trxID.objects.get(id = id1)
            correction.trx_id = t_id
            correction.status = 'pending'
            correction.save()
            inst = new_trx_id.objects.get(id = new_id)
            inst.delete()
            return redirect('home')
    else:
        form = OrederForm()
        form2 = ConfirmOrederForm()
        form3 = Correct_trx_ID()
        form4 = ConfirmOrederForm_btc()'''
    context = {
        'profile_info': model,
    }
    return render(request, 'home/dashboard.html', context)


@login_required
def upload_doc(request):
    if request.method == 'POST':

        formset = FileForm(request.POST or None, request.FILES or None)
        user = request.user
        if formset.is_valid():
            file = File.objects.get(user = user)
            #file = File(user=user, file=formset.cleaned_data['file'], file2=formset.cleaned_data['file2'])
            file.file = formset.cleaned_data['file']
            file.file2 = formset.cleaned_data['file2']
            file.save()
            corr = Profile_info.objects.get(user = user)
            corr.profile_status = 'pending'
            corr.save()
            return redirect('dashboard')

    else:
        formset = FileForm()

    context = {
        'formset': formset,
    }
    return render(request, 'home/doc_upload.html', context)

@staff_member_required
def admin_panel(request):
    user = request.user
    if user.is_staff:
        return render(request, 'home/admin_panel.html')
    else:
        return HttpResponseServerError()

@staff_member_required
def admin_pending_orders(request):
    user = request.user
    if user.is_staff:
        orders = order_with_trxID.objects.filter(status='pending')
        paginator = Paginator(orders, 15)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context = {
            'page_obj': page_obj,
        }
        return render(request, 'home/admin_pending_orders.html', context)
    else:
        return HttpResponseServerError()

@staff_member_required
def process_order_step1(request, order_id):
    user = request.user
    if user.is_staff:
        order = order_with_trxID.objects.get(belonging_order_id=order_id)
        admin_sending_accounts = our_ids.objects.filter(title = order.receive_at)
        if request.method == 'POST':
            instance = order_with_trxID.objects.get(belonging_order_id=order_id)
            form = ProcessFrom1(request.POST)
            form1 = Admin_sending_btc_wallet(request.POST)
            form2 = WalletAddressForm(request.POST)
            form3 = StatusForm(request.POST)
            if form.is_valid():
                data = request.POST.copy()
                status = data.get('status')
                instance = order_with_trxID.objects.get(belonging_order_id=order_id)
                Order_processed_By.objects.create(
                    title=instance.belonging_order_id,
                    processed_by=user,
                    made_status=status,
                    order=instance.belonging_order_id,
                )
                instance.order_processed_by = user.id
                instance.save()
                if status=='completed':
                    admin_received = float(data.get('admin_received'))
                    admin_sends = float(data.get('admin_sends'))
                    instance = order_with_trxID.objects.get(belonging_order_id = order_id)
                    instance.status = status
                    instance.admin_sending_account = data.get('admin_sending_acc')
                    instance.admin_transaction_id = data.get('admin_transaction_id')
                    instanceSend = reserve_balances_rates.objects.get(title=instance.sent_from)
                    instanceSend.reserve_am = instanceSend.reserve_am - instance.sent_amount
                    instanceRcv = reserve_balances_rates.objects.get(title=instance.receive_at)
                    instanceRcv.reserve_am = instanceRcv.reserve_am + instance.to_be_sent
                    ins_acc_send = our_ids.objects.filter(title=instance.sent_from).get(address=instance.admin_receiving_account)
                    ins_acc_send.reserve = ins_acc_send.reserve - instance.sent_amount
                    instance.sent_amount = admin_received
                    instance.to_be_sent = admin_sends
                    instanceSend.reserve_am = instanceSend.reserve_am + admin_received
                    instanceRcv.reserve_am = instanceRcv.reserve_am - admin_sends
                    ins_acc_send.reserve = ins_acc_send.reserve + admin_received
                    ins_acc_rcv = our_ids.objects.filter(title=instance.receive_at).get(address=instance.admin_sending_account)
                    ins_acc_rcv.reserve = ins_acc_rcv.reserve - admin_sends
                    ins_acc_rcv.send_count = ins_acc_rcv.send_count + 1
                    ins_acc_rcv.save()
                    total_cash_flow_instance_send = Actual_cash_flow_total.objects.get(title = instance.sent_from)
                    total_cash_flow_instance_rcv = Actual_cash_flow_total.objects.get(title = instance.receive_at)
                    total_cash_flow_instance_send.incoming = total_cash_flow_instance_send.incoming + admin_received
                    total_cash_flow_instance_rcv.outgoing = total_cash_flow_instance_rcv.outgoing + admin_sends
                    Actual_cash_flow_account_wise.objects.create(
                        title = instance.sent_from+'_'+instance.admin_receiving_account+'_'+str(instance.date_ordered),
                        gateway = instance.sent_from,
                        account_name = instance.admin_receiving_account,
                        incoming = instance.sent_amount,
                        outgoing = 0,
                        belonging_order_id = order_id,
                        time = datetime.datetime.now()
                    )
                    Actual_cash_flow_account_wise.objects.create(
                        title=instance.receive_at + '_' + instance.admin_sending_account + '_' + str(instance.date_ordered),
                        gateway=instance.receive_at,
                        account_name=instance.admin_sending_account,
                        incoming=0,
                        outgoing=instance.to_be_sent,
                        belonging_order_id=order_id,
                        time=datetime.datetime.now()
                    )
                    instance.save()
                    instanceSend.save()
                    instanceRcv.save()
                    total_cash_flow_instance_send.save()
                    total_cash_flow_instance_rcv.save()
                    ins_acc_send.save()
                    current_site = get_current_site(request)
                    mail_subject = 'Order Completed'
                    message = render_to_string('home/completed_order_email.html', {
                        'user': instance.user,
                        'order_id': order_id,
                        'domain': current_site.domain,
                        'sent_from': instance.sent_from,
                        'receive_at': instance.receive_at,
                        'sent_amount': instance.sent_amount,
                        'to_be_sent': instance.to_be_sent,
                        'send_unit': instance.send_unit,
                        'rcv_unit': instance.rcv_unit,
                        'rcv_account': instance.rcv_acount,
                        'admin_sending_account': instance.admin_sending_account,
                    })
                    to_email = instance.user.email
                    email = EmailMessage(
                        mail_subject, message, to=[to_email]
                    )
                    email.send()
                    return redirect('process_order_step2', order_id = order_id)
                elif status == 'invalid transaction id':
                    instance = order_with_trxID.objects.get(belonging_order_id=order_id)
                    instance.status = status
                    instance.save()
                    current_site = get_current_site(request)
                    mail_subject = 'Invalid transaction Id'
                    message = render_to_string('home/invalid_trxid_email.html', {
                        'user': instance.user,
                        'order_id': order_id,
                        'domain': current_site.domain,
                        'sent_from': instance.sent_from,
                        'receive_at': instance.receive_at,
                        'sent_amount': instance.sent_amount,
                        'to_be_sent': instance.to_be_sent,
                        'send_unit': instance.send_unit,
                        'rcv_unit': instance.rcv_unit,
                        'rcv_account': instance.rcv_acount,
                    })
                    to_email = instance.user.email
                    email = EmailMessage(
                        mail_subject, message, to=[to_email]
                    )
                    email.send()
                    return redirect('admin_pending_orders')
                elif status == 'canceled':
                    instance = order_with_trxID.objects.get(belonging_order_id=order_id)
                    instance.status = status
                    instance.save()
                    instanceSend = reserve_balances_rates.objects.get(title=instance.sent_from)
                    instanceSend.reserve_am = instanceSend.reserve_am - instance.sent_amount
                    instanceRcv = reserve_balances_rates.objects.get(title=instance.receive_at)
                    instanceRcv.reserve_am = instanceRcv.reserve_am + instance.to_be_sent
                    ins_acc_send = our_ids.objects.filter(title=instance.sent_from).get(
                        address=instance.admin_receiving_account)
                    ins_acc_send.reserve = ins_acc_send.reserve - instance.sent_amount
                    instance.save()
                    instanceSend.save()
                    instanceRcv.save()
                    ins_acc_send.save()
                    current_site = get_current_site(request)
                    mail_subject = 'Order Canceled'
                    message = render_to_string('home/order_canceled_email.html', {
                        'user': instance.user,
                        'order_id': order_id,
                        'domain': current_site.domain,
                        'sent_from': instance.sent_from,
                        'receive_at': instance.receive_at,
                        'sent_amount': instance.sent_amount,
                        'to_be_sent': instance.to_be_sent,
                        'send_unit': instance.send_unit,
                        'rcv_unit': instance.rcv_unit,
                        'rcv_account': instance.rcv_acount,
                    })
                    to_email = instance.user.email
                    email = EmailMessage(
                        mail_subject, message, to=[to_email]
                    )
                    email.send()
                    return redirect('admin_pending_orders')
                else:
                    return redirect('process_order_step1', order_id = order_id)
            if form.is_valid() and form1.is_valid():
                data = request.POST.copy()
                status = data.get('status')
                instance = order_with_trxID.objects.get(belonging_order_id=order_id)
                Order_processed_By.objects.create(
                    title=instance.belonging_order_id,
                    processed_by=user,
                    made_status=status,
                    order=instance.belonging_order_id,
                )
                instance.order_processed_by = user.id
                instance.save()
                if status=='completed':
                    admin_received = float(data.get('admin_received'))
                    admin_sends = float(data.get('admin_sends'))
                    instance = order_with_trxID.objects.get(belonging_order_id = order_id)
                    instance.status = status
                    instance.admin_sending_account = data.get('admin_sending_acc')
                    instance.admin_send_btc_wallet = data.get('wallet')
                    instance.admin_transaction_id = data.get('admin_transaction_id')
                    instanceSend = reserve_balances_rates.objects.get(title=instance.sent_from)
                    instanceSend.reserve_am = instanceSend.reserve_am - instance.sent_amount
                    instanceRcv = reserve_balances_rates.objects.get(title=instance.receive_at)
                    instanceRcv.reserve_am = instanceRcv.reserve_am + instance.to_be_sent
                    ins_acc_send = our_ids.objects.filter(title=instance.sent_from).get(address=instance.admin_receiving_account)
                    ins_acc_send.reserve = ins_acc_send.reserve - instance.sent_amount
                    instance.sent_amount = admin_received
                    instance.to_be_sent = admin_sends
                    instanceSend.reserve_am = instanceSend.reserve_am + admin_received
                    instanceRcv.reserve_am = instanceRcv.reserve_am - admin_sends
                    ins_acc_send.reserve = ins_acc_send.reserve + admin_received
                    ins_acc_rcv = our_ids.objects.filter(title=instance.receive_at).get(address=instance.admin_sending_account)
                    ins_acc_rcv.reserve = ins_acc_rcv.reserve - admin_sends
                    ins_acc_rcv.send_count = ins_acc_rcv.send_count + 1
                    ins_acc_rcv.save()
                    total_cash_flow_instance_send = Actual_cash_flow_total.objects.get(title = instance.sent_from)
                    total_cash_flow_instance_rcv = Actual_cash_flow_total.objects.get(title = instance.receive_at)
                    total_cash_flow_instance_send.incoming = total_cash_flow_instance_send.incoming + admin_received
                    total_cash_flow_instance_rcv.outgoing = total_cash_flow_instance_rcv.outgoing + admin_sends
                    Actual_cash_flow_account_wise.objects.create(
                        title = instance.sent_from+'_'+instance.admin_receiving_account+'_'+str(instance.date_ordered),
                        gateway = instance.sent_from,
                        account_name = instance.admin_rcv_btc_wallet,
                        incoming = instance.sent_amount,
                        outgoing = 0,
                        belonging_order_id = order_id,
                        time = datetime.datetime.now()
                    )
                    Actual_cash_flow_account_wise.objects.create(
                        title=instance.receive_at + '_' + instance.admin_sending_account + '_' + str(instance.date_ordered),
                        gateway=instance.receive_at,
                        account_name=instance.admin_send_btc_wallet,
                        incoming=0,
                        outgoing=instance.to_be_sent,
                        belonging_order_id=order_id,
                        time=datetime.datetime.now()
                    )
                    instance.save()
                    instanceSend.save()
                    instanceRcv.save()
                    total_cash_flow_instance_send.save()
                    total_cash_flow_instance_rcv.save()
                    ins_acc_send.save()
                    current_site = get_current_site(request)
                    mail_subject = 'Order Completed'
                    message = render_to_string('home/completed_order_email.html', {
                        'user': instance.user,
                        'order_id': order_id,
                        'domain': current_site.domain,
                        'sent_from': instance.sent_from,
                        'receive_at': instance.receive_at,
                        'sent_amount': instance.sent_amount,
                        'to_be_sent': instance.to_be_sent,
                        'send_unit': instance.send_unit,
                        'rcv_unit': instance.rcv_unit,
                        'rcv_account': instance.rcv_acount,
                        'admin_sending_account': instance.admin_sending_account,
                    })
                    to_email = instance.user.email
                    email = EmailMessage(
                        mail_subject, message, to=[to_email]
                    )
                    email.send()
                    return redirect('process_order_step2', order_id = order_id)
                elif status == 'invalid transaction id':
                    instance = order_with_trxID.objects.get(belonging_order_id=order_id)
                    instance.status = status
                    instance.save()
                    current_site = get_current_site(request)
                    mail_subject = 'Invalid transaction Id'
                    message = render_to_string('home/invalid_trxid_email.html', {
                        'user': instance.user,
                        'order_id': order_id,
                        'domain': current_site.domain,
                        'sent_from': instance.sent_from,
                        'receive_at': instance.receive_at,
                        'sent_amount': instance.sent_amount,
                        'to_be_sent': instance.to_be_sent,
                        'send_unit': instance.send_unit,
                        'rcv_unit': instance.rcv_unit,
                        'rcv_account': instance.rcv_acount,
                    })
                    to_email = instance.user.email
                    email = EmailMessage(
                        mail_subject, message, to=[to_email]
                    )
                    email.send()
                    return redirect('admin_pending_orders')
                elif status == 'canceled':
                    instance = order_with_trxID.objects.get(belonging_order_id=order_id)
                    instance.status = status
                    instance.save()
                    instanceSend = reserve_balances_rates.objects.get(title=instance.sent_from)
                    instanceSend.reserve_am = instanceSend.reserve_am - instance.sent_amount
                    instanceRcv = reserve_balances_rates.objects.get(title=instance.receive_at)
                    instanceRcv.reserve_am = instanceRcv.reserve_am + instance.to_be_sent
                    ins_acc_send = our_ids.objects.filter(title=instance.sent_from).get(
                        address=instance.admin_receiving_account)
                    ins_acc_send.reserve = ins_acc_send.reserve - instance.sent_amount
                    instance.save()
                    instanceSend.save()
                    instanceRcv.save()
                    ins_acc_send.save()
                    current_site = get_current_site(request)
                    mail_subject = 'Order Canceled'
                    message = render_to_string('home/order_canceled_email.html', {
                        'user': instance.user,
                        'order_id': order_id,
                        'domain': current_site.domain,
                        'sent_from': instance.sent_from,
                        'receive_at': instance.receive_at,
                        'sent_amount': instance.sent_amount,
                        'to_be_sent': instance.to_be_sent,
                        'send_unit': instance.send_unit,
                        'rcv_unit': instance.rcv_unit,
                        'rcv_account': instance.rcv_acount,
                    })
                    to_email = instance.user.email
                    email = EmailMessage(
                        mail_subject, message, to=[to_email]
                    )
                    email.send()
                    return redirect('admin_pending_orders')
                else:
                    return redirect('process_order_step1', order_id = order_id)
            if form2.is_valid() and form3.is_valid():
                data = request.POST.copy()
                instance = order_with_trxID.objects.get(belonging_order_id=order_id)
                Order_processed_By.objects.create(
                    title=instance.belonging_order_id,
                    processed_by=user,
                    made_status=status,
                    order=instance.belonging_order_id,
                )
                instance.order_processed_by = user.id
                instance.save()
                if data.get('status') == 'waiting for confirmation':
                    wallet_db_instance = BTC_wallet_address.objects.filter(belonging_order_id = order_id)
                    wallet = ''
                    if wallet_db_instance:
                        wallet_db_instance = BTC_wallet_address.objects.get(belonging_order_id = order_id)
                        wallet_db_instance.title = data.get('title')
                        wallet = wallet_db_instance.title
                        wallet_db_instance.save()
                    else:
                        wallet_instance = form2.save(commit=False)
                        wallet_instance.belonging_order_id = order_id
                        wallet = wallet_instance.title
                        wallet_instance.save()
                    status = data.get('status')
                    instance = order_with_trxID.objects.get(belonging_order_id=order_id)
                    instance.admin_receiving_account = wallet
                    instance.status = status
                    instance.save()
                    current_site = get_current_site(request)
                    mail_subject = 'BTC Wallet Address of ExonTime'
                    message = render_to_string('home/wallet_address_email.html', {
                        'user': instance.user,
                        'order_id': order_id,
                        'domain': current_site.domain,
                        'sent_from': instance.sent_from,
                        'receive_at': instance.receive_at,
                        'sent_amount': instance.sent_amount,
                        'to_be_sent': instance.to_be_sent,
                        'send_unit': instance.send_unit,
                        'rcv_unit': instance.rcv_unit,
                        'wallet_address': wallet,
                        'rcv_account': instance.rcv_acount,
                    })
                    to_email = instance.user.email
                    email = EmailMessage(
                        mail_subject, message, to=[to_email]
                    )
                    email.send()
                    return redirect('admin_pending_orders')
                else:
                    return redirect('process_order_step1', order_id = order_id)
        else:
            form = ProcessFrom1()
            form1 = Admin_sending_btc_wallet()
            form2 = WalletAddressForm()
            form3 = StatusForm()
        context = {
            'order': order,
            'form': form,
            'form1': form1,
            'form2': form2,
            'form3': form3,
            'admin_sending_accounts': admin_sending_accounts,
        }
        return render(request, 'home/process_order_step1.html', context)
    else:
        return HttpResponseServerError()

@staff_member_required
def process_order_step2(request, order_id):
    user = request.user
    if user.is_staff:
        order = order_with_trxID.objects.get(belonging_order_id=order_id)
        total_reserve = reserve_balances_rates.objects.get(title = order.receive_at)
        account_wise_reserve = our_ids.objects.filter(title = order.receive_at).get(address = order.admin_sending_account)
        if request.method == 'POST':
            form1 = ProcessFrom2(request.POST)
            form2 = ProcessFrom3(request.POST)
            if form1.is_valid() and form2.is_valid():
                data = request.POST.copy()
                total_reserve_amount = float(data.get('total_reserve_amount'))
                account_reserve_amount = float(data.get('account_reserve_amount'))
                total_instance = reserve_balances_rates.objects.get(title = order.receive_at)
                if total_instance.reserve_am != total_reserve_amount:
                    total_instance.reserve_am = total_reserve_amount
                account_instance = our_ids.objects.filter(title = order.receive_at).get(address = order.admin_sending_account)
                if account_instance.reserve != account_reserve_amount:
                    account_instance.reserve = account_reserve_amount
                total_instance.save()
                account_instance.save()
                return redirect('admin_pending_orders')
            if form1.is_valid() :
                data = request.POST.copy()
                total_reserve_amount = float(data.get('total_reserve_amount'))
                total_instance = reserve_balances_rates.objects.get(title = order.receive_at)
                if total_instance.reserve_am != total_reserve_amount:
                    total_instance.reserve_am = total_reserve_amount
                total_instance.save()
                return redirect('admin_pending_orders')
        else:
            form1 = ProcessFrom2()
            form2 = ProcessFrom3()
        if order.receive_at != 'btcusd':
            context = {
                'order': order,
                'total_reserve': total_reserve,
                'account_wise_reserve': account_wise_reserve,
                'form1': form1,
                'form2': form2,
            }
        else:
            context = {
                'order': order,
                'total_reserve': total_reserve,
                'account_wise_reserve': account_wise_reserve,
                'form1': form1,
                'form2': form2,
            }
        return render(request, 'home/process_order_step2.html', context)
    else:
        return HttpResponseServerError()

@staff_member_required
def btc_process_order_step2(request, order_id):
    user = request.user
    if user.is_staff:
        order = order_with_trxID.objects.get(belonging_order_id=order_id)
        total_reserve = reserve_balances_rates.objects.get(title = order.receive_at)
        account_wise_reserve = our_ids.objects.filter(title = order.receive_at).get(address = order.admin_sending_account)
        if request.method == 'POST':
            form1 = ProcessFrom2(request.POST)
            form2 = ProcessFrom3(request.POST)
            if form1.is_valid() and form2.is_valid():
                data = request.POST.copy()
                total_reserve_amount = float(data.get('total_reserve_amount'))
                account_reserve_amount = float(data.get('account_reserve_amount'))
                total_instance = reserve_balances_rates.objects.get(title = order.receive_at)
                if total_instance.reserve_am != total_reserve_amount:
                    total_instance.reserve_am = total_reserve_amount
                account_instance = our_ids.objects.filter(title = order.receive_at).get(address = order.admin_sending_account)
                if account_instance.reserve != account_reserve_amount:
                    account_instance.reserve = account_reserve_amount
                total_instance.save()
                account_instance.save()
                return redirect('admin_waiting_orders')
            if form1.is_valid() :
                data = request.POST.copy()
                total_reserve_amount = float(data.get('total_reserve_amount'))
                total_instance = reserve_balances_rates.objects.get(title = order.receive_at)
                if total_instance.reserve_am != total_reserve_amount:
                    total_instance.reserve_am = total_reserve_amount
                total_instance.save()
                return redirect('admin_waiting_orders')
        else:
            form1 = ProcessFrom2()
            form2 = ProcessFrom3()
        if order.receive_at != 'btcusd':
            context = {
                'order': order,
                'total_reserve': total_reserve,
                'account_wise_reserve': account_wise_reserve,
                'form1': form1,
                'form2': form2,
            }
        else:
            context = {
                'order': order,
                'total_reserve': total_reserve,
                'account_wise_reserve': account_wise_reserve,
                'form1': form1,
                'form2': form2,
            }
        return render(request, 'home/process_order_step2.html', context)
    else:
        return HttpResponseServerError()

@staff_member_required
def admin_waiting_orders(request):
    user = request.user
    if user.is_staff:
        orders = order_with_trxID.objects.filter(Q(status='waiting for confirmation') | Q(status = 'confirmed'))
        paginator = Paginator(orders, 15)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context = {
            'page_obj': page_obj,
        }
        return render(request, 'home/admin_waiting_orders.html', context)
    else:
        return HttpResponseServerError()

@staff_member_required
def btc_order_processing(request, order_id):
    user = request.user
    if user.is_staff:
        order = order_with_trxID.objects.get(belonging_order_id=order_id)
        admin_sending_accounts = our_ids.objects.filter(title = order.receive_at)
        if request.method == 'POST':
            form = ProcessFrom1(request.POST)
            form1 = Admin_sending_btc_wallet(request.POST)
            if form.is_valid():
                data = request.POST.copy()
                status = data.get('status')
                instance = order_with_trxID.objects.get(belonging_order_id=order_id)
                Order_processed_By.objects.create(
                    title=instance.belonging_order_id,
                    processed_by=user,
                    made_status=status,
                    order=instance.belonging_order_id,
                )
                instance.order_processed_by = user.id
                instance.save()
                if status == 'completed':
                    admin_received = float(data.get('admin_received'))
                    admin_sends = float(data.get('admin_sends'))
                    instance = order_with_trxID.objects.get(belonging_order_id = order_id)
                    instance.status = status
                    instance.admin_sending_account = data.get('admin_sending_acc')
                    instance.admin_transaction_id = data.get('admin_transaction_id')
                    instanceSend = reserve_balances_rates.objects.get(title=instance.sent_from)
                    instanceSend.reserve_am = instanceSend.reserve_am - instance.sent_amount
                    instanceRcv = reserve_balances_rates.objects.get(title=instance.receive_at)
                    instanceRcv.reserve_am = instanceRcv.reserve_am + instance.to_be_sent
                    ins_acc_send = our_ids.objects.filter(title=instance.sent_from).get(
                        address=instance.admin_receiving_account)
                    ins_acc_send.reserve = ins_acc_send.reserve - instance.sent_amount
                    instance.sent_amount = admin_received
                    instance.to_be_sent = admin_sends
                    instanceSend.reserve_am = instanceSend.reserve_am + admin_received
                    instanceRcv.reserve_am = instanceRcv.reserve_am - admin_sends
                    ins_acc_send.reserve = ins_acc_send.reserve + admin_received
                    ins_acc_rcv = our_ids.objects.filter(title=instance.receive_at).get(
                        address=instance.admin_sending_account)
                    ins_acc_rcv.reserve = ins_acc_rcv.reserve - admin_sends
                    ins_acc_rcv.send_count = ins_acc_rcv.send_count + 1
                    ins_acc_rcv.save()
                    total_cash_flow_instance_send = Actual_cash_flow_total.objects.get(title = instance.sent_from)
                    total_cash_flow_instance_rcv = Actual_cash_flow_total.objects.get(title = instance.receive_at)
                    total_cash_flow_instance_send.incoming = total_cash_flow_instance_send.incoming + admin_received
                    total_cash_flow_instance_rcv.outgoing = total_cash_flow_instance_rcv.outgoing + admin_sends
                    Actual_cash_flow_account_wise.objects.create(
                        title = instance.sent_from+'_'+instance.admin_receiving_account+'_'+str(instance.date_ordered),
                        gateway = instance.sent_from,
                        account_name = instance.admin_receiving_account,
                        incoming = instance.sent_amount,
                        outgoing = 0,
                        belonging_order_id = order_id,
                        time = datetime.datetime.now()
                    )
                    Actual_cash_flow_account_wise.objects.create(
                        title=instance.receive_at + '_' + instance.admin_sending_account + '_' + str(instance.date_ordered),
                        gateway=instance.receive_at,
                        account_name=instance.admin_sending_account,
                        incoming=0,
                        outgoing=instance.to_be_sent,
                        belonging_order_id=order_id,
                        time=datetime.datetime.now()
                    )
                    instance.save()
                    instanceSend.save()
                    instanceRcv.save()
                    total_cash_flow_instance_send.save()
                    total_cash_flow_instance_rcv.save()
                    current_site = get_current_site(request)
                    mail_subject = 'Order Completed'
                    message = render_to_string('home/completed_order_email.html', {
                        'user': instance.user,
                        'order_id': order_id,
                        'domain': current_site.domain,
                        'sent_from': instance.sent_from,
                        'receive_at': instance.receive_at,
                        'sent_amount': instance.sent_amount,
                        'to_be_sent': instance.to_be_sent,
                        'send_unit': instance.send_unit,
                        'rcv_unit': instance.rcv_unit,
                        'rcv_account': instance.rcv_acount,
                        'admin_sending_account': instance.admin_sending_account,
                    })
                    to_email = instance.user.email
                    email = EmailMessage(
                        mail_subject, message, to=[to_email]
                    )
                    email.send()
                    return redirect('btc_order_processing_step2', order_id = order_id)
                elif status == 'invalid transaction id':
                    '''instance = order_with_trxID.objects.get(belonging_order_id=order_id)
                    instance.status = status
                    instance.save()
                    current_site = get_current_site(request)
                    mail_subject = 'Invalid transaction Id'
                    message = render_to_string('home/invalid_trxid_email.html', {
                        'user': instance.user,
                        'order_id': order_id,
                        'domain': current_site.domain,
                        'sent_from': instance.sent_from,
                        'receive_at': instance.receive_at,
                        'sent_amount': instance.sent_amount,
                        'to_be_sent': instance.to_be_sent,
                        'send_unit': instance.send_unit,
                        'rcv_unit': instance.rcv_unit,
                        'rcv_account': instance.rcv_acount,
                    })
                    to_email = instance.user.email
                    email = EmailMessage(
                        mail_subject, message, to=[to_email]
                    )
                    email.send()'''
                    #return redirect('admin_waiting_orders')
                    return redirect('btc_order_processing', order_id=order_id)
                elif status == 'canceled':
                    instance = order_with_trxID.objects.get(belonging_order_id=order_id)
                    instance.status = status
                    instance.save()
                    instanceSend = reserve_balances_rates.objects.get(title=instance.sent_from)
                    instanceSend.reserve_am = instanceSend.reserve_am - instance.sent_amount
                    instanceRcv = reserve_balances_rates.objects.get(title=instance.receive_at)
                    instanceRcv.reserve_am = instanceRcv.reserve_am + instance.to_be_sent
                    ins_acc_send = our_ids.objects.filter(title=instance.sent_from).get(
                        address=instance.admin_receiving_account)
                    ins_acc_send.reserve = ins_acc_send.reserve - instance.sent_amount
                    instance.save()
                    instanceSend.save()
                    instanceRcv.save()
                    ins_acc_send.save()
                    current_site = get_current_site(request)
                    mail_subject = 'Order Canceled'
                    message = render_to_string('home/order_canceled_email.html', {
                        'user': instance.user,
                        'order_id': order_id,
                        'domain': current_site.domain,
                        'sent_from': instance.sent_from,
                        'receive_at': instance.receive_at,
                        'sent_amount': instance.sent_amount,
                        'to_be_sent': instance.to_be_sent,
                        'send_unit': instance.send_unit,
                        'rcv_unit': instance.rcv_unit,
                        'rcv_account': instance.rcv_acount,
                    })
                    to_email = instance.user.email
                    email = EmailMessage(
                        mail_subject, message, to=[to_email]
                    )
                    email.send()
                    return redirect('admin_waiting_orders')
                else:
                    return redirect('btc_order_processing', order_id = order_id)

            if form.is_valid() and form1.is_valid():
                data = request.POST.copy()
                status = data.get('status')
                instance = order_with_trxID.objects.get(belonging_order_id=order_id)
                Order_processed_By.objects.create(
                    title=instance.belonging_order_id,
                    processed_by=user,
                    made_status=status,
                    order=instance.belonging_order_id,
                )
                instance.order_processed_by = user.id
                instance.save()
                if status=='completed':
                    admin_received = float(data.get('admin_received'))
                    admin_sends = float(data.get('admin_sends'))
                    instance = order_with_trxID.objects.get(belonging_order_id = order_id)
                    instance.status = status
                    instance.admin_sending_account = data.get('admin_sending_acc')
                    instance.admin_send_btc_wallet = data.get('wallet')
                    instance.admin_transaction_id = data.get('admin_transaction_id')
                    instanceSend = reserve_balances_rates.objects.get(title=instance.sent_from)
                    instanceSend.reserve_am = instanceSend.reserve_am - instance.sent_amount
                    instanceRcv = reserve_balances_rates.objects.get(title=instance.receive_at)
                    instanceRcv.reserve_am = instanceRcv.reserve_am + instance.to_be_sent
                    ins_acc_send = our_ids.objects.filter(title=instance.sent_from).get(
                        address=instance.admin_receiving_account)
                    ins_acc_send.reserve = ins_acc_send.reserve - instance.sent_amount
                    instance.sent_amount = admin_received
                    instance.to_be_sent = admin_sends
                    instanceSend.reserve_am = instanceSend.reserve_am + admin_received
                    instanceRcv.reserve_am = instanceRcv.reserve_am - admin_sends
                    ins_acc_send.reserve = ins_acc_send.reserve + admin_received
                    ins_acc_rcv = our_ids.objects.filter(title=instance.receive_at).get(
                        address=instance.admin_sending_account)
                    ins_acc_rcv.reserve = ins_acc_rcv.reserve - admin_sends
                    ins_acc_rcv.send_count = ins_acc_rcv.send_count + 1
                    ins_acc_rcv.save()
                    total_cash_flow_instance_send = Actual_cash_flow_total.objects.get(title = instance.sent_from)
                    total_cash_flow_instance_rcv = Actual_cash_flow_total.objects.get(title = instance.receive_at)
                    total_cash_flow_instance_send.incoming = total_cash_flow_instance_send.incoming + admin_received
                    total_cash_flow_instance_rcv.outgoing = total_cash_flow_instance_rcv.outgoing + admin_sends
                    Actual_cash_flow_account_wise.objects.create(
                        title = instance.sent_from+'_'+instance.admin_receiving_account+'_'+str(instance.date_ordered),
                        gateway = instance.sent_from,
                        account_name = instance.admin_receiving_account,
                        incoming = instance.sent_amount,
                        outgoing = 0,
                        belonging_order_id = order_id,
                        time = datetime.datetime.now()
                    )
                    Actual_cash_flow_account_wise.objects.create(
                        title=instance.receive_at + '_' + instance.admin_sending_account + '_' + str(instance.date_ordered),
                        gateway=instance.receive_at,
                        account_name=instance.admin_sending_account,
                        incoming=0,
                        outgoing=instance.to_be_sent,
                        belonging_order_id=order_id,
                        time=datetime.datetime.now()
                    )
                    instance.save()
                    instanceSend.save()
                    instanceRcv.save()
                    total_cash_flow_instance_send.save()
                    total_cash_flow_instance_rcv.save()
                    current_site = get_current_site(request)
                    mail_subject = 'Order Completed'
                    message = render_to_string('home/completed_order_email.html', {
                        'user': instance.user,
                        'order_id': order_id,
                        'domain': current_site.domain,
                        'sent_from': instance.sent_from,
                        'receive_at': instance.receive_at,
                        'sent_amount': instance.sent_amount,
                        'to_be_sent': instance.to_be_sent,
                        'send_unit': instance.send_unit,
                        'rcv_unit': instance.rcv_unit,
                        'rcv_account': instance.rcv_acount,
                        'admin_sending_account': instance.admin_sending_account,
                    })
                    to_email = instance.user.email
                    email = EmailMessage(
                        mail_subject, message, to=[to_email]
                    )
                    email.send()
                    return redirect('btc_order_processing_step2', order_id = order_id)
                elif status == 'invalid transaction id':
                    '''instance = order_with_trxID.objects.get(belonging_order_id=order_id)
                    instance.status = status
                    instance.save()
                    current_site = get_current_site(request)
                    mail_subject = 'Invalid transaction Id'
                    message = render_to_string('home/invalid_trxid_email.html', {
                        'user': instance.user,
                        'order_id': order_id,
                        'domain': current_site.domain,
                        'sent_from': instance.sent_from,
                        'receive_at': instance.receive_at,
                        'sent_amount': instance.sent_amount,
                        'to_be_sent': instance.to_be_sent,
                        'send_unit': instance.send_unit,
                        'rcv_unit': instance.rcv_unit,
                        'rcv_account': instance.rcv_acount,
                    })
                    to_email = instance.user.email
                    email = EmailMessage(
                        mail_subject, message, to=[to_email]
                    )
                    email.send()'''
                    #return redirect('admin_waiting_orders')
                    return redirect('btc_order_processing', order_id=order_id)
                elif status == 'canceled':
                    instance = order_with_trxID.objects.get(belonging_order_id=order_id)
                    instance.status = status
                    instance.save()
                    instanceSend = reserve_balances_rates.objects.get(title=instance.sent_from)
                    instanceSend.reserve_am = instanceSend.reserve_am - instance.sent_amount
                    instanceRcv = reserve_balances_rates.objects.get(title=instance.receive_at)
                    instanceRcv.reserve_am = instanceRcv.reserve_am + instance.to_be_sent
                    ins_acc_send = our_ids.objects.filter(title=instance.sent_from).get(
                        address=instance.admin_receiving_account)
                    ins_acc_send.reserve = ins_acc_send.reserve - instance.sent_amount
                    instance.save()
                    instanceSend.save()
                    instanceRcv.save()
                    ins_acc_send.save()
                    current_site = get_current_site(request)
                    mail_subject = 'Order Canceled'
                    message = render_to_string('home/order_canceled_email.html', {
                        'user': instance.user,
                        'order_id': order_id,
                        'domain': current_site.domain,
                        'sent_from': instance.sent_from,
                        'receive_at': instance.receive_at,
                        'sent_amount': instance.sent_amount,
                        'to_be_sent': instance.to_be_sent,
                        'send_unit': instance.send_unit,
                        'rcv_unit': instance.rcv_unit,
                        'rcv_account': instance.rcv_acount,
                    })
                    to_email = instance.user.email
                    email = EmailMessage(
                        mail_subject, message, to=[to_email]
                    )
                    email.send()
                    return redirect('admin_waiting_orders')
                else:
                    return redirect('btc_order_processing', order_id = order_id)
        else:
            form = ProcessFrom1()
            form1 = Admin_sending_btc_wallet()
        context = {
            'order': order,
            'form': form,
            'form1': form1,
            'admin_sending_accounts': admin_sending_accounts,
        }
        return render(request, 'home/btc_order_processing.html', context)
    else:
        return HttpResponseServerError()

@login_required
def admin_search_order(request):
    user = request.user
    if user.is_staff:
        return render(request, 'home/admin_search_order.html')
    else:
        return HttpResponseServerError()

@staff_member_required
def admin_unconfirmed_order(request):
    user = request.user
    if user.is_staff:
        orders = orders_without_trxID.objects.all()
        invalid_trx_id = order_with_trxID.objects.filter(status='invalid transaction id')
        unconfirmed_orders = order_with_trxID.objects.filter(status = 'unconfirmed')
        context = {
            'orders': orders,
            'invalid_trx_id': invalid_trx_id,
            'unconfirmed_orders': unconfirmed_orders,
        }
        return render(request, 'home/admin_unconfirmed_order.html', context)
    else:
        return HttpResponseServerError()

class AdminCompletedOrder(ListView, LoginRequiredMixin):
    model = order_with_trxID
    template_name = 'home/admin_completed_order.html'
    context_object_name = 'orders'
    ordering = ['-belonging_order_id']
    paginate_by = 15
    def get_queryset(self):
        #user = get_object_or_404(User, username=self.kwargs.get('username'))
        return order_with_trxID.objects.filter(status='completed').order_by('-belonging_order_id')

    @method_decorator(staff_member_required)
    def dispatch(self, request, *args, **kwargs):
        return super(AdminCompletedOrder, self).dispatch(request, *args, **kwargs)

class AdminCancceledOrder(ListView, LoginRequiredMixin):
    model = order_with_trxID
    template_name = 'home/admin_canceled_order.html'
    context_object_name = 'orders'
    ordering = ['-belonging_order_id']
    paginate_by = 15
    def get_queryset(self):
        #user = get_object_or_404(User, username=self.kwargs.get('username'))
        return order_with_trxID.objects.filter(status='canceled').order_by('-belonging_order_id')

    @method_decorator(staff_member_required)
    def dispatch(self, request, *args, **kwargs):
        return super(AdminCancceledOrder, self).dispatch(request, *args, **kwargs)

@staff_member_required
def admin_help(request):
    user = request.user
    if user.is_staff:
        texts = Contact_us.objects.filter(state = 'unseen')
        paginator = Paginator(texts, 15)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context = {
            'page_obj': page_obj,
        }
        return render(request, 'home/admin_help.html', context)
    else:
        return HttpResponseServerError()

@staff_member_required
def admin_reply(request, msg_id):
    user = request.user
    if user.is_staff:
        text = Contact_us.objects.get(id = msg_id)
        if request.method == 'POST':
            form = ReplyFrom(request.POST)
            if form.is_valid():
                data = request.POST.copy()
                msg = data.get('msg')
                current_site = get_current_site(request)
                mail_subject = 'Reply to your Query'
                text.state = 'replied'
                text.save()
                message = render_to_string('home/query_reply.html', {
                    'user': text.user,
                    'msg': msg,
                    'domain': current_site.domain,
                })
                to_email = text.email
                email = EmailMessage(
                    mail_subject, message, to=[to_email]
                )
                email.send()
                return redirect('admin_help')
        else:
            form = ReplyFrom()
        context = {
            'text': text,
            'form': form,
        }
        return render(request, 'home/admin_reply.html', context)
    else:
        return HttpResponseServerError()

@staff_member_required
def admin_actual_flow(request):
    user = request.user
    if user.is_staff:
        flows = Actual_cash_flow_total.objects.all()
        context = {
            'flows': flows,
        }
        return render(request, 'home/admin_actual_flow.html', context)
    else:
        return HttpResponseServerError()

@staff_member_required
def admin_reserve(request):
    user = request.user
    if user.is_staff:
        acc_reserves = our_ids.objects.all()
        reserves = reserve_balances_rates.objects.all()
        context = {
            'acc_reserves': acc_reserves,
            'reserves': reserves,
        }
        return render(request, 'home/admin_reserve.html', context)
    else:
        return HttpResponseServerError()

@staff_member_required
def admin_review_msg_approval(request):
    user = request.user
    if user.is_staff:
        reviews = Review_msg.objects.filter(state = 'hide')
        paginator = Paginator(reviews, 15)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        if request.method == 'POST':
            form = Review_msg_approval_form(request.POST)
            if form.is_valid():
                data = request.POST.copy()
                state = data.get('state')
                review_id = int(data.get('review_id'))
                instance = Review_msg.objects.get(id = review_id)
                instance.state = state
                instance.save()
                return redirect('admin_review_approval')
        else:
            form = Review_msg_approval_form()
        context = {
            'page_obj': page_obj,
            'form': form,
        }
        return render(request, 'home/admin_review_approval.html', context)
    else:
        return HttpResponseServerError()

@staff_member_required
def admin_verify_user(request):
    user = request.user
    if user.is_staff:
        users = Profile_info.objects.filter(profile_status = 'pending')
        paginator = Paginator(users, 3)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        if request.method == 'POST':
            form = ProfileStatusForm(request.POST)
            if form.is_valid():
                data = request.POST.copy()
                profile_status = data.get('profile_status')
                user_id = int(data.get('user_id'))
                instance = Profile_info.objects.get(user_id = user_id)
                instance.profile_status = profile_status
                instance.save()
                return redirect('verify_users')
        else:
            form = ProfileStatusForm()
        context = {
            'page_obj': page_obj,
            'form': form,
        }
        return render(request, 'home/admin_verify_users.html', context)
    else:
        return HttpResponseServerError()