from django.shortcuts import render, redirect
from django.contrib import messages
from django_daraja.mpesa.core import MpesaClient # type: ignore
from django.contrib.auth.decorators import login_required

@login_required
def mpesa_pay(request):
    """View to initiate M-Pesa STK Push."""
    if request.method == 'POST':
        phone_number = request.POST.get('phone')
        amount = request.POST.get('amount')
        
        # 1. Format Phone Number (Must start with 254)
        if phone_number.startswith('0'):
            phone_number = '254' + phone_number[1:]
        elif phone_number.startswith('+254'):
            phone_number = phone_number[1:]
        
        # 2. Initialize Client
        cl = MpesaClient()
        
        # 3. Callback URL (For demo, we use a placeholder or your render link)
        callback_url = 'https://water-management-system-ouep.onrender.com/api/mpesa/callback/'
        
        account_reference = 'WaterConnect'
        transaction_desc = 'Donation'
        
        try:
            # 4. Trigger the STK Push
            response = cl.stk_push(phone_number, int(amount), account_reference, transaction_desc, callback_url)
            
            # 5. Success Message
            if response.response_code == "0":
                messages.success(request, f"STK Push sent to {phone_number}. Check your phone to pay!")
            else:
                messages.error(request, f"Failed: {response.error_message}")
                
        except Exception as e:
            messages.error(request, f"M-Pesa Error: {str(e)}")
            
        return redirect('mpesa_pay')

    return render(request, 'waterapp/pay.html')