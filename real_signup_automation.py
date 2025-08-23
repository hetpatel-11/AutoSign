"""
Real signup automation using AgentMail for email verification.
This script can sign up for various services and automatically handle verification codes.
"""

import asyncio
import os
import sys
from browser_use.llm import ChatAnthropic
from browser_use import Agent, BrowserSession, BrowserProfile
from agentmail_helper import AgentMailHelper
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

class RealSignupAutomation:
    def __init__(self):
        self.agentmail = AgentMailHelper()
        self.email = None
        self.verification_code = None
        
    def setup_browser(self):
        """Setup persistent browser profile"""
        user_data_dir = Path.home() / ".config" / "browseruse" / "profiles" / "persistent"
        user_data_dir.mkdir(parents=True, exist_ok=True)
        
        browser_profile = BrowserProfile(
            user_data_dir=str(user_data_dir),
            keep_alive=True,
            headless=False,
            viewport={"width": 1280, "height": 800},
        )
        
        return BrowserSession(browser_profile=browser_profile)
    
    def setup_llm(self):
        """Setup Anthropic LLM"""
        return ChatAnthropic(
            model="claude-sonnet-4-0",
            api_key=os.environ['ANTHROPIC_API_KEY']
        )
    
    async def get_verification_code(self, timeout=120):
        """Wait for and extract verification code from AgentMail"""
        print(f"📧 Waiting for verification code in {self.email}...")
        print("⏳ This may take up to 2 minutes...")
        
        code = await self.agentmail.wait_for_verification_code(timeout=timeout)
        if code:
            print(f"✅ Verification code received: {code}")
            return code
        else:
            print("❌ No verification code received within timeout")
            return None
    
    async def signup_with_verification(self, signup_url, signup_task, verification_task):
        """
        Complete signup process with email verification
        
        Args:
            signup_url: URL of the signup page
            signup_task: Task description for initial signup
            verification_task: Task description for entering verification code
        """
        try:
            # Setup AgentMail
            self.email = self.agentmail.setup()
            print(f"📧 Using email: {self.email}")
            
            # Setup browser and LLM
            browser_session = self.setup_browser()
            llm = self.setup_llm()
            
            # Step 1: Initial signup (focus only on the signup website)
            print(f"\n🚀 Step 1: Starting signup at {signup_url}")
            signup_agent = Agent(
                task=f"{signup_task} Use email: {self.email}. CRITICAL: Stay ONLY on the signup website ({signup_url}), do NOT navigate to any other websites including AgentMail. The email verification will be handled separately.",
                llm=llm,
                browser_session=browser_session,
            )
            
            signup_result = await signup_agent.run()
            print(f"✅ Signup completed: {signup_result}")
            
            # Step 2: Wait for verification code (using API, not browser)
            print(f"\n📧 Step 2: Waiting for verification email...")
            self.verification_code = await self.get_verification_code()
            
            if not self.verification_code:
                print("❌ Failed to get verification code")
                return False
            
            # Step 3: Enter verification code
            print(f"\n🔐 Step 3: Entering verification code: {self.verification_code}")
            verification_agent = Agent(
                task=f"{verification_task} Use code: {self.verification_code}. Stay on the same website and find the verification input field.",
                llm=llm,
                browser_session=browser_session,
            )
            
            verification_result = await verification_agent.run()
            print(f"✅ Verification completed: {verification_result}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error during signup: {e}")
            return False

async def main():
    """Main function to run signup automation"""
    print("🚀 Real Signup Automation with AgentMail")
    print("=" * 50)
    
    # Get signup details from command line
    if len(sys.argv) < 2:
        print("Usage: python real_signup_automation.py <service>")
        print("\nAvailable services:")
        print("  reddit     - Sign up for Reddit")
        print("  twitter    - Sign up for Twitter/X")
        print("  github     - Sign up for GitHub")
        print("  discord    - Sign up for Discord")
        print("  custom     - Custom signup (provide URL)")
        print("\nExample: python real_signup_automation.py reddit")
        sys.exit(1)
    
    service = sys.argv[1].lower()
    
    # Service configurations
    services = {
        'reddit': {
            'url': 'https://www.reddit.com/register/',
            'signup_task': 'Go to Reddit signup page and create a new account. Fill in username, password, and email. Complete the signup process and wait for email verification step. IMPORTANT: Stay only on Reddit website, do not navigate to any other websites.',
            'verification_task': 'Find the email verification input field and enter the verification code. Submit the form to complete verification.'
        },
        'twitter': {
            'url': 'https://twitter.com/i/flow/signup',
            'signup_task': 'Go to Twitter signup page and create a new account. Fill in name, email, and password. Complete the signup process and wait for email verification step. IMPORTANT: Stay only on Twitter website, do not navigate to any other websites.',
            'verification_task': 'Find the verification code input field and enter the code. Submit to complete verification.'
        },
        'github': {
            'url': 'https://github.com/signup',
            'signup_task': 'Go to GitHub signup page and create a new account. Fill in username, email, and password. Complete the signup process and wait for email verification step. IMPORTANT: Stay only on GitHub website, do not navigate to any other websites.',
            'verification_task': 'Find the verification code input field and enter the code. Submit to complete verification.'
        },
        'discord': {
            'url': 'https://discord.com/register',
            'signup_task': 'Go to Discord signup page and create a new account. Fill in email, username, and password. Complete the signup process and wait for email verification step. IMPORTANT: Stay only on Discord website, do not navigate to any other websites.',
            'verification_task': 'Find the verification code input field and enter the code. Submit to complete verification.'
        }
    }
    
    if service == 'custom':
        if len(sys.argv) < 4:
            print("For custom signup, provide URL and task:")
            print("python real_signup_automation.py custom <url> <signup_task>")
            sys.exit(1)
        
        custom_url = sys.argv[2]
        custom_task = " ".join(sys.argv[3:])
        
        service_config = {
            'url': custom_url,
            'signup_task': custom_task,
            'verification_task': 'Find the verification code input field and enter the code. Submit to complete verification.'
        }
    elif service in services:
        service_config = services[service]
    else:
        print(f"❌ Unknown service: {service}")
        print("Available services:", ", ".join(services.keys()))
        sys.exit(1)
    
    # Run the signup automation
    automation = RealSignupAutomation()
    
    print(f"🎯 Service: {service.upper()}")
    print(f"🌐 URL: {service_config['url']}")
    print(f"📝 Task: {service_config['signup_task']}")
    print("\n" + "=" * 50)
    
    success = await automation.signup_with_verification(
        service_config['url'],
        service_config['signup_task'],
        service_config['verification_task']
    )
    
    if success:
        print("\n🎉 Signup automation completed successfully!")
        print(f"📧 Email used: {automation.email}")
        print(f"🔐 Verification code: {automation.verification_code}")
    else:
        print("\n❌ Signup automation failed")

if __name__ == "__main__":
    asyncio.run(main())
