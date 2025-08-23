"""
Test script to verify the most recent verification code function.
"""

from simple_agentmail_api import get_most_recent_verification_code

def test_latest_code():
    """Test getting the most recent verification code"""
    print("🔍 Testing Most Recent Verification Code Function")
    print("=" * 50)
    
    code = get_most_recent_verification_code()
    
    if code:
        print(f"\n✅ Most recent verification code: {code}")
    else:
        print("\n❌ No verification code found")

if __name__ == "__main__":
    test_latest_code()
