from django_daraja.mpesa.core import MpesaClient # type: ignore
import logging
logger = logging.getLogger(__name__)

def trigger_stk_push(phone_number, amount, account_reference="WaterConnect", transaction_desc="Payment"):
    """
    A reusable helper function that communicates with Safaricom.
    It handles phone formatting and the STK Push request.
    
    Args:
        phone_number (str): The user's phone (e.g., "0712...")
        amount (int/str): The amount to pay
        account_reference (str): Text that appears on the user's statement
        transaction_desc (str): Internal description
        
    Returns:
        Response object from MpesaClient or None if failed.
    """
    
    phone_number = str(phone_number).strip()
    if phone_number.startswith('0'):
        phone_number = '254' + phone_number[1:]
    elif phone_number.startswith('+254'):
        phone_number = phone_number[1:]
        
    cl = MpesaClient()
    
    callback_url = 'https://water-management-system-ouep.onrender.com/api/mpesa/callback/'
    
    try:
        response = cl.stk_push(
            phone_number, 
            int(amount), 
            account_reference, 
            transaction_desc, 
            callback_url
        )
        return response
        
    except Exception as e:
        logger.error(f"M-Pesa STK Push Failed: {str(e)}")
        print(f"M-Pesa Error: {str(e)}")
        return None