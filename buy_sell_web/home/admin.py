from django.contrib import admin
from .models import Profile_info, order_with_trxID, orders_without_trxID, \
    new_trx_id, reserve_balances_rates, File, our_ids, Contact_us, Review_msg, \
    Actual_cash_flow_total, Actual_cash_flow_account_wise, We_send, We_rcv, \
    BTC_wallet_address

admin.site.register(Profile_info)
admin.site.register(order_with_trxID)
admin.site.register(orders_without_trxID)
admin.site.register(new_trx_id)
admin.site.register(reserve_balances_rates)
admin.site.register(File)
admin.site.register(our_ids)
admin.site.register(Contact_us)
admin.site.register(Review_msg)
admin.site.register(Actual_cash_flow_total)
admin.site.register(Actual_cash_flow_account_wise)
admin.site.register(BTC_wallet_address)
admin.site.register(We_send)
admin.site.register(We_rcv)