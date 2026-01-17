import os
from dotenv import load_dotenv
from agency import create_agency

load_dotenv()

def smoke_test():
    print("Checking environment...")
    if not os.getenv("OPENAI_API_KEY"):
        print("[ERROR] OPENAI_API_KEY not found in .env")
        return
    
    print("Initializing Agency...")
    try:
        agency = create_agency()
        print(f"[OK] Agency '{agency.name}' initialized successfully.")
        print("Agents involved:")
        for agent in agency.agents:
            if hasattr(agent, 'name'):
                print(f" - {agent.name}")
            else:
                print(f" - {agent}")
            
        print("\n[SUCCESS] Agency is ready for local execution.")
    except Exception as e:
        print(f"[ERROR] Failed to initialize agency: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    smoke_test()
