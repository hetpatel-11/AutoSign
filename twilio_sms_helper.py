import requests
import os
import time
import re
from datetime import datetime

class TwilioSMSHelper:
    """Helper class to integrate Twilio SMS with AutoSign"""
    
    def __init__(self, api_base_url="http://localhost:5000"):
        self.api_base_url = api_base_url
        self.twilio_configured = self._check_twilio_status()
    
    def _check_twilio_status(self):
        """Check if Twilio is properly configured"""
        try:
            response = requests.get(f"{self.api_base_url}/status")
            if response.status_code == 200:
                data = response.json()
                return data.get('twilio_configured', False)
        except:
            pass
        return False
    
    def send_verification_code(self, phone_number, code=None):
        """Send verification code via SMS"""
        if not self.twilio_configured:
            print("❌ Twilio not configured. Please set up your Twilio credentials.")
            return None
        
        try:
            payload = {
                'phone_number': phone_number,
                'code': code  # If None, server will generate one
            }
            
            response = requests.post(f"{self.api_base_url}/send-code", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ SMS sent to {phone_number}")
                print(f"📱 Message SID: {data.get('message_sid')}")
                return data.get('code')
            else:
                print(f"❌ Failed to send SMS: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Error sending SMS: {str(e)}")
            return None
    
    def get_latest_verification_code(self, phone_number, max_wait_time=60):
        """Get the latest verification code for a phone number"""
        if not self.twilio_configured:
            print("❌ Twilio not configured")
            return None
        
        start_time = time.time()
        
        while time.time() - start_time < max_wait_time:
            try:
                response = requests.get(f"{self.api_base_url}/get-latest-code/{phone_number}")
                
                if response.status_code == 200:
                    data = response.json()
                    code = data.get('code')
                    timestamp = data.get('timestamp')
                    
                    if code:
                        print(f"✅ Found verification code: {code}")
                        print(f"📅 Received at: {timestamp}")
                        return code
                
                # Wait 2 seconds before checking again
                time.sleep(2)
                
            except Exception as e:
                print(f"⚠️  Error checking for code: {str(e)}")
                time.sleep(2)
        
        print(f"⏰ Timeout: No verification code received within {max_wait_time} seconds")
        return None
    
    def verify_code(self, phone_number, code):
        """Verify a submitted code"""
        if not self.twilio_configured:
            print("❌ Twilio not configured")
            return False
        
        try:
            payload = {
                'phone_number': phone_number,
                'code': code
            }
            
            response = requests.post(f"{self.api_base_url}/verify-code", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('verified'):
                    print("✅ Code verified successfully!")
                    return True
                else:
                    print("❌ Invalid verification code")
                    return False
            else:
                print(f"❌ Verification failed: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Error verifying code: {str(e)}")
            return False
    
    def clear_all_codes(self):
        """Clear all stored verification codes (for testing)"""
        try:
            response = requests.post(f"{self.api_base_url}/clear-codes")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ {data.get('message')}")
                return True
            else:
                print(f"❌ Failed to clear codes: {response.text}")
                return False
        except Exception as e:
            print(f"❌ Error clearing codes: {str(e)}")
            return False

# Integration with AutoSign
def integrate_with_autosign():
    """Example of how to integrate Twilio SMS with AutoSign"""
    
    # Initialize the SMS helper
    sms_helper = TwilioSMSHelper()
    
    if not sms_helper.twilio_configured:
        print("❌ Please start the Flask app and configure Twilio first!")
        return
    
    # Example phone number (replace with actual number)
    phone_number = "+1234567890"  # Replace with your phone number
    
    print("🚀 AutoSign + Twilio SMS Integration Demo")
    print("=" * 50)
    
    # Step 1: Send verification code
    print("\n📱 Step 1: Sending verification code...")
    code = sms_helper.send_verification_code(phone_number)
    
    if code:
        print(f"📤 Code sent: {code}")
        
        # Step 2: Wait for user to receive and respond
        print("\n⏳ Step 2: Waiting for SMS response...")
        print("Please check your phone and respond with the code")
        
        # Step 3: Get the latest code (in real scenario, user would text back)
        received_code = sms_helper.get_latest_verification_code(phone_number, max_wait_time=30)
        
        if received_code:
            # Step 4: Verify the code
            print(f"\n🔍 Step 3: Verifying code: {received_code}")
            if sms_helper.verify_code(phone_number, received_code):
                print("🎉 SMS verification successful! AutoSign can now proceed.")
            else:
                print("❌ SMS verification failed!")
        else:
            print("❌ No verification code received")
    else:
        print("❌ Failed to send verification code")

if __name__ == "__main__":
    # Test the SMS helper
    integrate_with_autosign()
