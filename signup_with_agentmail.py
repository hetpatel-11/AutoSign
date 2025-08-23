"""
Automated signup using AgentMail for email verification codes and browser-use for automation.
This script will:
1. Create an AgentMail inbox
2. Use browser automation to sign up on a website
3. Retrieve verification codes from AgentMail
4. Complete the signup process automatically
"""

from browser_use import Agent, BrowserSession, BrowserProfile
from browser_use.llm import ChatAnthropic
from dotenv import load_dotenv
import asyncio
import os
import sys
import time
import re
from pathlib import Path

# You'll need to install agentmail: pip install agentmail
try:
    from agentmail import AgentMail
except ImportError:
    print("Please install agentmail: pip install agentmail")
    sys.exit(1)

load_dotenv()

class SignupAutomation:
    def __init__(self):
        self.agentmail_client = None
        self.inbox_id = None
        self.email_address = None
        self.verification_code = None
        
    async def setup_agentmail(self):
        """Setup AgentMail client and create/get inbox"""
        api_key = os.environ.get('AGENTMAIL_API_KEY')
        if not api_key:
            print("❌ Please set AGENTMAIL_API_KEY environment variable")
            sys.exit(1)
            
        self.agentmail_client = AgentMail(api_key=api_key)
        
        # Create a new inbox or use existing one
        try:
            # You can either create a new inbox or use an existing one
            # For now, we'll use a placeholder - you'll need to create one via AgentMail dashboard
            self.inbox_id = os.environ.get('AGENTMAIL_INBOX_ID')
            if not self.inbox_id:
                print("❌ Please set AGENTMAIL_INBOX_ID environment variable")
                print("Create an inbox at https://app.agentmail.to and get the inbox ID")
                sys.exit(1)
                
            # Get inbox details to get the email address
            inbox = self.agentmail_client.inboxes.get(inbox_id=self.inbox_id)
            self.email_address = f"{inbox['inbox_id']}@agentmail.to"
            print(f"✅ Using AgentMail inbox: {self.email_address}")
            
        except Exception as e:
            print(f"❌ Error setting up AgentMail: {e}")
            sys.exit(1)
    
    async def wait_for_verification_email(self, timeout=60):
        """Wait for verification email and extract the code"""
        print(f"⏳ Waiting for verification email (timeout: {timeout}s)...")
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                # Get messages from the inbox
                messages = self.agentmail_client.inboxes.messages.list(inbox_id=self.inbox_id)
                
                for message in messages:
                    # Look for verification emails
                    if self._is_verification_email(message):
                        code = self._extract_verification_code(message)
                        if code:
                            self.verification_code = code
                            print(f"✅ Found verification code: {code}")
                            return code
                            
            except Exception as e:
                print(f"⚠️ Error checking messages: {e}")
                
            await asyncio.sleep(5)  # Check every 5 seconds
            
        print("❌ No verification code found within timeout")
        return None
    
    def _is_verification_email(self, message):
        """Check if message is a verification email"""
        subject = message.get('subject', '').lower()
        text = message.get('text', '').lower()
        
        verification_keywords = [
            'verification', 'verify', 'confirm', 'activation', 
            'code', 'otp', 'pin', 'security code'
        ]
        
        return any(keyword in subject or keyword in text for keyword in verification_keywords)
    
    def _extract_verification_code(self, message):
        """Extract verification code from email content"""
        text = message.get('text', '')
        html = message.get('html', '')
        
        # Common patterns for verification codes
        patterns = [
            r'\b\d{4,8}\b',  # 4-8 digit codes
            r'verification code[:\s]*(\d{4,8})',
            r'code[:\s]*(\d{4,8})',
            r'(\d{4,8})',  # Any 4-8 digit number
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1) if len(match.groups()) > 0 else match.group(0)
        
        return None
    
    async def run_signup_automation(self, signup_task):
        """Run the complete signup automation"""
        print("🚀 Starting automated signup process...")
        
        # Setup AgentMail
        await self.setup_agentmail()
        
        # Create browser session with persistent profile
        user_data_dir = Path.home() / ".config" / "browseruse" / "profiles" / "persistent"
        user_data_dir.mkdir(parents=True, exist_ok=True)
        
        browser_profile = BrowserProfile(
            user_data_dir=str(user_data_dir),
            keep_alive=True,
        )
        
        browser_session = BrowserSession(
            browser_profile=browser_profile,
        )
        
        # Setup LLM
        llm = ChatAnthropic(
            model="claude-sonnet-4-0",
            api_key=os.environ['ANTHROPIC_API_KEY']
        )
        
        # Create the signup task with email address
        enhanced_task = f"{signup_task} Use this email address: {self.email_address}"
        
        print(f"📧 Using email: {self.email_address}")
        print(f"🎯 Task: {enhanced_task}")
        
        # Create agent for signup
        agent = Agent(
            task=enhanced_task,
            llm=llm,
            browser_session=browser_session,
        )
        
        try:
            # Start signup process
            print("🔄 Starting signup process...")
            result = await agent.run()
            print(f"✅ Signup process completed: {result}")
            
            # Wait for verification email
            verification_code = await self.wait_for_verification_email()
            
            if verification_code:
                # Create agent for verification
                verification_task = f"Enter the verification code: {verification_code}"
                print(f"🔐 Entering verification code: {verification_code}")
                
                verification_agent = Agent(
                    task=verification_task,
                    llm=llm,
                    browser_session=browser_session,
                )
                
                verification_result = await verification_agent.run()
                print(f"✅ Verification completed: {verification_result}")
                
            else:
                print("⚠️ No verification code received")
                
        except Exception as e:
            print(f"❌ Error during signup: {e}")

async def main():
    if len(sys.argv) < 2:
        print("Usage: python signup_with_agentmail.py \"signup task description\"")
        print("Example: python signup_with_agentmail.py \"Go to example.com and sign up for an account\"")
        sys.exit(1)
    
    signup_task = " ".join(sys.argv[1:])
    
    automation = SignupAutomation()
    await automation.run_signup_automation(signup_task)

if __name__ == "__main__":
    asyncio.run(main())
