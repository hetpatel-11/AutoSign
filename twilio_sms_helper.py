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
    
    def process_verification_code(self, phone_number, code):
        """Process verification code when endpoint is hit"""
        try:
            payload = {
                'phone_number': phone_number,
                'code': code
            }
            
            response = requests.post(f"{self.api_base_url}/process-code", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Verification code processed for {phone_number}: {code}")
                return data.get('code')
            else:
                print(f"❌ Failed to process code: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Error processing code: {str(e)}")
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
    """Example of how AutoSign gets verification codes via Twilio webhook"""
    
    # Initialize the SMS helper
    sms_helper = TwilioSMSHelper()
    
    # Example phone number
    phone_number = "+1234567890"  # Replace with your phone number
    
    print("🚀 AutoSign + Twilio Webhook Integration Demo")
    print("=" * 50)
    
    print("\n📱 Step 1: User gets verification code from website")
    print("User should text the verification code to your Twilio number")
    print(f"Twilio number: {os.getenv('TWILIO_PHONE_NUMBER', 'Your Twilio Number')}")
    
    print("\n⏳ Step 2: Waiting for Twilio webhook to receive SMS...")
    print("AutoSign is waiting for the verification code...")
    
    # Wait for webhook to receive the code
    received_code = sms_helper.get_latest_verification_code(phone_number, max_wait_time=60)
    
    if received_code:
        print(f"\n✅ Step 3: Code received via webhook: {received_code}")
        
        # Verify the code
        print(f"\n🔍 Step 4: Verifying code: {received_code}")
        if sms_helper.verify_code(phone_number, received_code):
            print("🎉 Verification successful! AutoSign can now proceed with signup.")
        else:
            print("❌ Verification failed!")
    else:
        print("❌ No verification code received from Twilio webhook")
        print("Make sure user texted the code to your Twilio number")

if __name__ == "__main__":
    # Test the SMS helper
    integrate_with_autosign()
