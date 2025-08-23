# AgentMail + Browser Automation Setup Guide

This guide shows you how to set up automated signup with email verification using AgentMail and browser-use.

## 🚀 Quick Start

### 1. Get AgentMail API Key
1. Go to [AgentMail Dashboard](https://app.agentmail.to)
2. Sign up and get your API key
3. Create an inbox and note the inbox ID

### 2. Set Environment Variables
```bash
export AGENTMAIL_API_KEY="your_agentmail_api_key_here"
export AGENTMAIL_INBOX_ID="your_inbox_id_here"
```

### 3. Use the Automated Signup Script
```bash
python signup_with_agentmail.py "Go to example.com and sign up for an account"
```

## 📋 How It Works

1. **Setup**: Creates AgentMail inbox and gets email address
2. **Signup**: Uses browser automation to fill signup form with AgentMail email
3. **Wait**: Monitors AgentMail inbox for verification emails
4. **Verify**: Automatically extracts verification code and completes signup

## 🔧 Available Scripts

### `signup_with_agentmail.py` - Complete Automation
Full automated signup with email verification:
```bash
python signup_with_agentmail.py "Go to twitter.com and sign up for an account"
```

### `agentmail_helper.py` - Helper Functions
Use with your existing `test.py` script:
```python
from agentmail_helper import get_agentmail_email, get_verification_code

# Get email for signup
email = get_agentmail_email()

# Wait for verification code
code = await get_verification_code()
```

## 📧 AgentMail Features Used

Based on the [AgentMail API documentation](https://docs.agentmail.to/api-reference/inboxes/messages/get):

- **Get Inbox**: Retrieve inbox details and email address
- **List Messages**: Monitor inbox for new emails
- **Get Message**: Extract verification codes from email content
- **Real-time**: Automatically detect verification emails

## 🎯 Example Workflow

```bash
# 1. Set up environment
export AGENTMAIL_API_KEY="your_key"
export AGENTMAIL_INBOX_ID="your_inbox"

# 2. Run automated signup
python signup_with_agentmail.py "Go to github.com and create a new account"

# 3. Script will:
#    - Use AgentMail email for signup
#    - Wait for verification email
#    - Extract verification code
#    - Complete signup automatically
```

## 🔍 Verification Code Detection

The script automatically detects verification codes using:
- **Patterns**: 4-8 digit codes, OTP, PIN numbers
- **Keywords**: "verification", "confirm", "activation", "code"
- **Formats**: Plain text and HTML email content

## 🛠️ Customization

You can customize:
- **Timeout**: How long to wait for verification emails
- **Patterns**: Custom regex patterns for different code formats
- **Keywords**: Add specific keywords for your target websites

## 📞 Support

- [AgentMail Documentation](https://docs.agentmail.to)
- [AgentMail API Reference](https://docs.agentmail.to/api-reference)
- [Browser-use Documentation](https://docs.browser-use.com)
