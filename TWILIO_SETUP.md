# 📱 Twilio SMS Setup for AutoSign

This guide will help you set up Twilio SMS integration for AutoSign to handle phone verification codes.

## 🚀 Quick Setup (5 Minutes)

### 1. Create Twilio Account
1. Go to [Twilio Console](https://console.twilio.com)
2. Sign up for a free account (you get $15 credit)
3. Verify your email and phone number

### 2. Get Your Credentials
1. In Twilio Console, go to **Account Info**
2. Copy your **Account SID** and **Auth Token**
3. Go to **Phone Numbers** → **Manage** → **Active numbers**
4. Buy a phone number (or use trial number)

### 3. Set Environment Variables
```bash
export TWILIO_ACCOUNT_SID="your_account_sid_here"
export TWILIO_AUTH_TOKEN="your_auth_token_here"
export TWILIO_PHONE_NUMBER="+1234567890"  # Your Twilio number
```

### 4. Install Dependencies
```bash
pip install flask twilio
```

### 5. Start the Flask App
```bash
python app.py
```

## 🔧 Detailed Configuration

### Twilio Phone Number Setup
1. **Buy a Number**: Go to **Phone Numbers** → **Buy a number**
2. **Choose Features**: Select SMS capability
3. **Configure Webhook**: Set webhook URL to `https://your-domain.com/webhook`
4. **Save Configuration**: Click "Save configuration"

### Webhook Configuration
For local development, use ngrok:
```bash
# Install ngrok
brew install ngrok  # macOS
# or download from https://ngrok.com

# Start ngrok tunnel
ngrok http 5000

# Use the ngrok URL as your webhook
# Example: https://abc123.ngrok.io/webhook
```

### Production Deployment
For production, deploy to:
- **Heroku**: `git push heroku main`
- **Railway**: Connect your GitHub repo
- **DigitalOcean**: Deploy with App Platform

## 📱 API Endpoints

### Send Verification Code
```bash
curl -X POST http://localhost:5000/send-code \
  -H "Content-Type: application/json" \
  -d '{"phone_number": "+1234567890"}'
```

### Verify Code
```bash
curl -X POST http://localhost:5000/verify-code \
  -H "Content-Type: application/json" \
  -d '{"phone_number": "+1234567890", "code": "123456"}'
```

### Get Latest Code
```bash
curl http://localhost:5000/get-latest-code/+1234567890
```

### Check Status
```bash
curl http://localhost:5000/status
```

## 🔗 Integration with AutoSign

### Option 1: Use the Helper Class
```python
from twilio_sms_helper import TwilioSMSHelper

# Initialize SMS helper
sms_helper = TwilioSMSHelper()

# Send verification code
code = sms_helper.send_verification_code("+1234567890")

# Get latest code (for AutoSign integration)
latest_code = sms_helper.get_latest_verification_code("+1234567890")
```

### Option 2: Direct API Calls
```python
import requests

# Send code
response = requests.post("http://localhost:5000/send-code", 
                        json={"phone_number": "+1234567890"})

# Get code
response = requests.get("http://localhost:5000/get-latest-code/+1234567890")
code = response.json()["code"]
```

## 🧪 Testing

### Test SMS Sending
```bash
python twilio_sms_helper.py
```

### Test Webhook (with ngrok)
1. Start ngrok: `ngrok http 5000`
2. Update Twilio webhook URL
3. Send SMS to your Twilio number
4. Check Flask app logs for incoming messages

### Manual Testing
```bash
# Start Flask app
python app.py

# In another terminal, test endpoints
curl http://localhost:5000/status
curl -X POST http://localhost:5000/send-code \
  -H "Content-Type: application/json" \
  -d '{"phone_number": "+1234567890"}'
```

## 🔒 Security Considerations

### Environment Variables
- Never commit API keys to git
- Use `.env` file for local development
- Use environment variables in production

### Rate Limiting
- Twilio has rate limits (1 SMS/second for trial)
- Implement your own rate limiting for production

### Phone Number Verification
- Verify phone numbers before sending SMS
- Implement proper error handling

## 💰 Pricing

### Twilio SMS Pricing
- **Trial Account**: $15 free credit
- **US Numbers**: ~$1/month per number
- **SMS**: ~$0.0079 per message (US)
- **International**: Varies by country

### Cost Estimation
- 100 SMS/month = ~$0.79
- 1000 SMS/month = ~$7.90
- Perfect for hackathon demos!

## 🐛 Troubleshooting

### Common Issues

**"Twilio not configured"**
- Check environment variables are set
- Verify Account SID and Auth Token

**"Phone number not verified"**
- Verify your phone number in Twilio Console
- Use verified numbers for testing

**"Webhook not receiving messages"**
- Check ngrok tunnel is active
- Verify webhook URL in Twilio Console
- Check Flask app is running

**"Rate limit exceeded"**
- Wait 1 second between SMS sends
- Upgrade to paid account for higher limits

### Debug Mode
```bash
# Enable debug logging
export FLASK_DEBUG=1
python app.py
```

## 🎯 Next Steps

1. **Test with AutoSign**: Integrate SMS verification into your signup flow
2. **Add Phone Number Input**: Modify AutoSign to ask for phone numbers
3. **Implement Fallback**: Use SMS as backup to email verification
4. **Production Ready**: Deploy to cloud platform with proper SSL

## 📞 Support

- **Twilio Docs**: [https://www.twilio.com/docs](https://www.twilio.com/docs)
- **Twilio Support**: [https://support.twilio.com](https://support.twilio.com)
- **AutoSign Issues**: Create issue in your GitHub repo

---

**Ready to add SMS verification to AutoSign! 🚀**
