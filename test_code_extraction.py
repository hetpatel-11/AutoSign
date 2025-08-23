"""
Test script to check verification code extraction from AgentMail.
"""

from agentmail_helper import get_latest_verification_code, AgentMailHelper

def test_code_extraction():
    """Test the verification code extraction"""
    print("🔍 Testing Verification Code Extraction...")
    
    # Test the latest verification code
    code = get_latest_verification_code()
    if code:
        print(f"✅ Latest verification code: {code}")
    else:
        print("❌ No verification code found")
    
    # Test with the helper class
    helper = AgentMailHelper()
    helper.setup()
    
    try:
        messages_response = helper.client.inboxes.messages.list(
            inbox_id=helper.inbox_id
        )
        
        print(f"\n📧 Found {len(messages_response.messages)} messages in inbox")
        
        for i, message in enumerate(messages_response.messages, 1):
            print(f"\n📨 Message {i}:")
            print(f"   Subject: {getattr(message, 'subject', 'No subject')}")
            print(f"   Preview: {getattr(message, 'preview', 'No preview')}")
            
            if helper._is_verification_email(message):
                print("   ✅ Detected as verification email")
                code = helper._extract_verification_code(message)
                if code:
                    print(f"   🔐 Extracted code: {code}")
                else:
                    print("   ❌ No code extracted")
            else:
                print("   ❌ Not a verification email")
                
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_code_extraction()
