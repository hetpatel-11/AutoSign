from browser_use.llm import ChatAnthropic
from browser_use import Agent, BrowserSession, BrowserProfile
from dotenv import load_dotenv
from pathlib import Path
import os
import asyncio
import sys

load_dotenv()

async def main():
    # Get task from command line arguments
    if len(sys.argv) < 2:
        print("Usage: python test.py \"your task here\"")
        print("Example: python test.py \"Go to Google and search for Python tutorials\"")
        print("Example: python test.py \"Check the weather on weather.com\"")
        sys.exit(1)
    
    # Get the task from command line arguments
    task = " ".join(sys.argv[1:])
    print(f"🎯 Task: {task}")
    print("Starting browser automation...")
    
    # Create persistent browser profile
    user_data_dir = Path.home() / ".config" / "browseruse" / "profiles" / "persistent"
    user_data_dir.mkdir(parents=True, exist_ok=True)
    
    browser_profile = BrowserProfile(
        user_data_dir=str(user_data_dir),
        keep_alive=True,
    )
    
    browser_session = BrowserSession(
        browser_profile=browser_profile,
    )
    
    llm = ChatAnthropic(
        model="claude-sonnet-4-0",
        api_key=os.environ['ANTHROPIC_API_KEY']
    )
    
    agent = Agent(
        task=task,
        llm=llm,
        browser_session=browser_session,
    )
    
    try:
        result = await agent.run()
        print("\n✅ Task completed!")
        print(f"Result: {result}")
    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())