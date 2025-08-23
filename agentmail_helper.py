"""
Helper functions for AgentMail integration with browser-use.
Provides reusable functions for email verification automation.
"""

import asyncio
import re
import os
from agentmail import AgentMail

class AgentMailHelper:
    def __init__(self):
        self.api_key = os.environ.get('AGENTMAIL_API_KEY')
        self.inbox_id = os.environ.get('AGENTMAIL_INBOX_ID')
        self.client = None
        
    def setup(self):
        """Setup AgentMail client and return the email address"""
        if not self.api_key:
            raise Exception("❌ AGENTMAIL_API_KEY not set")
        if not self.inbox_id:
            raise Exception("❌ AGENTMAIL_INBOX_ID not set")
            
        self.client = AgentMail(api_key=self.api_key)
        return self.inbox_id
    
    async def wait_for_verification_code(self, timeout=60, check_interval=5):
        """
        Wait for a verification code email and extract the code.
        
        Args:
            timeout: Total time to wait in seconds
            check_interval: How often to check for new messages
            
        Returns:
            The verification code if found, None otherwise
        """
        if not self.client:
            self.setup()
            
        start_time = asyncio.get_event_loop().time()
        last_checked_time = start_time
        
        while (asyncio.get_event_loop().time() - start_time) < timeout:
            try:
                # Get messages from the inbox (synchronous call)
                messages_response = self.client.inboxes.messages.list(
                    inbox_id=self.inbox_id
                )
                
                # Check each message for verification codes, prioritizing newer messages
                for message in messages_response.messages:
                    if self._is_verification_email(message):
                        code = self._extract_verification_code(message)
                        if code:
                            print(f"📧 Found verification email: {getattr(message, 'subject', 'No subject')}")
                            print(f"📄 Content preview: {getattr(message, 'preview', 'No preview')}")
                            return code
                            
            except Exception as e:
                print(f"⚠️ Error checking messages: {e}")
                
            # Wait before checking again
            await asyncio.sleep(check_interval)
            
        return None
    
    def get_latest_verification_code(self):
        """
        Get the most recent verification code from the inbox.
        Returns the code if found, None otherwise.
        """
        if not self.client:
            self.setup()
            
        try:
            messages_response = self.client.inboxes.messages.list(
                inbox_id=self.inbox_id
            )
            
            # Check messages in reverse order (newest first)
            for message in reversed(messages_response.messages):
                if self._is_verification_email(message):
                    code = self._extract_verification_code(message)
                    if code:
                        print(f"📧 Found verification email: {getattr(message, 'subject', 'No subject')}")
                        print(f"📄 Content preview: {getattr(message, 'preview', 'No preview')}")
                        return code
                        
        except Exception as e:
            print(f"⚠️ Error getting latest verification code: {e}")
            
        return None
    
    def _is_verification_email(self, message):
        """Check if a message is a verification email"""
        # Check subject for verification keywords
        subject = getattr(message, 'subject', '') or ''
        subject_lower = subject.lower()
        
        verification_keywords = [
            'verification', 'verify', 'confirm', 'confirmation',
            'code', 'otp', 'pin', 'activate', 'activation'
        ]
        
        if any(keyword in subject_lower for keyword in verification_keywords):
            return True
            
        # Check message content for verification keywords
        content = self._get_message_content(message)
        if content:
            content_lower = content.lower()
            if any(keyword in content_lower for keyword in verification_keywords):
                return True
                
        return False
    
    def _extract_verification_code(self, message):
        """Extract verification code from message content"""
        content = self._get_message_content(message)
        if not content:
            return None
            
        # Common patterns for verification codes - flexible length
        patterns = [
            r'launch code[:\s]*(\d+)',  # GitHub specific - check first
            r'(\d+)[^0-9]*launch',  # GitHub specific - check first
            r'verification code[:\s]*(\d+)',  # "verification code: 123456"
            r'code[:\s]*(\d+)',  # "code: 123456"
            r'(\d+)[^0-9]*is your',  # "123456 is your code"
            r'enter[^0-9]*(\d+)',  # "enter code 123456"
            r'(\d+)[^0-9]*to verify',  # "123456 to verify"
            r'(\d+)[^0-9]*verification',  # "123456 verification"
            r'(\d+)',  # General pattern - check last
        ]
        
        # Try all patterns for flexible length codes
        for pattern in patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                code = match.group(1)
                # Validate it's a reasonable verification code (2+ digits)
                if code.isdigit() and len(code) >= 2:
                    return code
                    
        return None
    
    def _get_message_content(self, message):
        """Get the text content from a message, handling different attribute names"""
        # Based on debug output, the content is in 'preview'
        if hasattr(message, 'preview') and message.preview:
            return message.preview
            
        # Fallback to other possible attributes
        content_attributes = ['text', 'body', 'content', 'message', 'html', 'plain_text']
        
        for attr in content_attributes:
            if hasattr(message, attr):
                content = getattr(message, attr)
                if content:
                    return content
                    
        return None

# Global helper instance
_agentmail_helper = AgentMailHelper()

def get_agentmail_email():
    """Get the AgentMail email address"""
    return _agentmail_helper.setup()

async def get_verification_code(timeout=60):
    """Wait for and return a verification code"""
    return await _agentmail_helper.wait_for_verification_code(timeout=timeout)

def get_latest_verification_code():
    """Get the most recent verification code from the inbox without waiting"""
    return _agentmail_helper.get_latest_verification_code()
