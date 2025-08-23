from flask import Flask, request, jsonify
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse
import os
import re
from datetime import datetime
import json

app = Flask(__name__)

# Twilio Configuration
TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
TWILIO_PHONE_NUMBER = os.getenv('TWILIO_PHONE_NUMBER')

# Initialize Twilio client
client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN) if TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN else None

# In-memory storage for verification codes (in production, use a database)
verification_codes = {}

@app.route('/')
def home():
    """Home page with API documentation"""
    return '''
    <h1>🚀 AutoSign SMS API</h1>
    <p>Twilio-powered SMS verification for AutoSign</p>
    
    <h2>📱 API Endpoints:</h2>
    <ul>
        <li><strong>POST /send-code</strong> - Send verification code via SMS</li>
        <li><strong>POST /verify-code</strong> - Verify received code</li>
        <li><strong>POST /webhook</strong> - Twilio webhook for incoming SMS</li>
        <li><strong>GET /status</strong> - Check API status</li>
    </ul>
    
    <h2>🔧 Setup:</h2>
    <p>Set environment variables:</p>
    <ul>
        <li>TWILIO_ACCOUNT_SID</li>
        <li>TWILIO_AUTH_TOKEN</li>
        <li>TWILIO_PHONE_NUMBER</li>
    </ul>
    '''

@app.route('/status')
def status():
    """Check API status and Twilio configuration"""
    twilio_configured = bool(TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN and TWILIO_PHONE_NUMBER)
    
    return jsonify({
        'status': 'running',
        'twilio_configured': twilio_configured,
        'timestamp': datetime.now().isoformat(),
        'verification_codes_count': len(verification_codes)
    })

@app.route('/send-code', methods=['POST'])
def send_verification_code():
    """Send verification code via SMS"""
    if not client:
        return jsonify({'error': 'Twilio not configured'}), 500
    
    data = request.get_json()
    if not data or 'phone_number' not in data:
        return jsonify({'error': 'phone_number is required'}), 400
    
    phone_number = data['phone_number']
    code = data.get('code') or generate_verification_code()
    
    try:
        # Send SMS with verification code
        message = client.messages.create(
            body=f"Your AutoSign verification code is: {code}",
            from_=TWILIO_PHONE_NUMBER,
            to=phone_number
        )
        
        # Store the code with timestamp
        verification_codes[phone_number] = {
            'code': code,
            'timestamp': datetime.now().isoformat(),
            'message_sid': message.sid
        }
        
        return jsonify({
            'success': True,
            'message_sid': message.sid,
            'phone_number': phone_number,
            'code': code  # In production, don't return the code
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/verify-code', methods=['POST'])
def verify_code():
    """Verify a received code"""
    data = request.get_json()
    if not data or 'phone_number' not in data or 'code' not in data:
        return jsonify({'error': 'phone_number and code are required'}), 400
    
    phone_number = data['phone_number']
    submitted_code = data['code']
    
    if phone_number not in verification_codes:
        return jsonify({'error': 'No verification code found for this phone number'}), 404
    
    stored_data = verification_codes[phone_number]
    stored_code = stored_data['code']
    
    if submitted_code == stored_code:
        # Remove the code after successful verification
        del verification_codes[phone_number]
        return jsonify({
            'success': True,
            'verified': True,
            'message': 'Code verified successfully'
        })
    else:
        return jsonify({
            'success': False,
            'verified': False,
            'message': 'Invalid verification code'
        })

@app.route('/webhook', methods=['POST'])
def twilio_webhook():
    """Handle incoming SMS from Twilio webhook"""
    # Get the message details from Twilio
    incoming_message = request.values.get('Body', '').strip()
    from_number = request.values.get('From', '')
    
    # Extract verification code from incoming message
    code = extract_verification_code(incoming_message)
    
    if code:
        # Store the received code
        verification_codes[from_number] = {
            'code': code,
            'timestamp': datetime.now().isoformat(),
            'source': 'incoming_sms'
        }
        
        # Respond to Twilio
        resp = MessagingResponse()
        resp.message("✅ Verification code received and stored!")
        return str(resp)
    else:
        # Respond to Twilio
        resp = MessagingResponse()
        resp.message("❌ No verification code found in message")
        return str(resp)

@app.route('/get-latest-code/<phone_number>')
def get_latest_code(phone_number):
    """Get the latest verification code for a phone number (for AutoSign integration)"""
    if phone_number not in verification_codes:
        return jsonify({'error': 'No verification code found'}), 404
    
    stored_data = verification_codes[phone_number]
    return jsonify({
        'phone_number': phone_number,
        'code': stored_data['code'],
        'timestamp': stored_data['timestamp']
    })

def generate_verification_code(length=6):
    """Generate a random verification code"""
    import random
    return ''.join([str(random.randint(0, 9)) for _ in range(length)])

def extract_verification_code(message):
    """Extract verification code from SMS message"""
    # Common patterns for verification codes
    patterns = [
        r'(\d{4,8})',  # 4-8 digit codes
        r'code[:\s]*(\d+)',  # "code: 123456"
        r'verification[:\s]*(\d+)',  # "verification: 123456"
        r'(\d+)[^0-9]*is your',  # "123456 is your code"
        r'enter[^0-9]*(\d+)',  # "enter code 123456"
    ]
    
    for pattern in patterns:
        match = re.search(pattern, message, re.IGNORECASE)
        if match:
            code = match.group(1)
            if code.isdigit() and len(code) >= 4:
                return code
    
    return None

@app.route('/clear-codes', methods=['POST'])
def clear_codes():
    """Clear all stored verification codes (for testing)"""
    global verification_codes
    count = len(verification_codes)
    verification_codes = {}
    return jsonify({
        'success': True,
        'message': f'Cleared {count} verification codes'
    })

if __name__ == '__main__':
    # Check if Twilio is configured
    if not TWILIO_ACCOUNT_SID or not TWILIO_AUTH_TOKEN or not TWILIO_PHONE_NUMBER:
        print("⚠️  Warning: Twilio not fully configured!")
        print("Set these environment variables:")
        print("  - TWILIO_ACCOUNT_SID")
        print("  - TWILIO_AUTH_TOKEN") 
        print("  - TWILIO_PHONE_NUMBER")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
