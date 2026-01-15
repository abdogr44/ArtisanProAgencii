import os
from dotenv import load_dotenv
from agency_swarm import Agency
from social_media_writer import social_media_writer

load_dotenv()

def test_marketing_bridge_post():
    """
    Test that the SocialMediaWriter creates a 'Bridge Post' with a Soft CTA
    when asked about silence and the app.
    """
    print("Testing Bridge Post (App Promotion)...")
    
    # direct interaction with the agent object (bypassing agency for unit test)
    # But usually we use the agent directly or a demo agency.
    # Let's simple create an agency with just this agent to test the prompt.
    
    agency = Agency(social_media_writer)
    
    # Request that should trigger a Bridge Post for the App
    response = agency.get_completion(
        "Write a short post about the noise of the city and how the Athar App helps. make it a bridge post."
    )
    
    print("\n--- AGENT RESPONSE ---\n")
    print(response)
    print("\n----------------------\n")
    
    content = response.lower()
    
    # Validation
    checks = {
        "Has CTA": any(cw in content for cw in ["link", "bio", "app", "download", "carry"]),
        "Is Poetic": len(content.split()) < 100, # Athar style is short
        "No Hard Sell": "buy now" not in content
    }
    
    for check, passed in checks.items():
        print(f"{check}: {'✅ PASS' if passed else '❌ FAIL'}")

if __name__ == "__main__":
    test_marketing_bridge_post()
