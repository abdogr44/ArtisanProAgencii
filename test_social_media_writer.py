from agency import create_agency
import time

def test_social_media_writer():
    print("Initializing agency...")
    try:
        agency = create_agency()
        
        print("Agency initialized. Testing SocialMediaWriter...")
        # Send a message to the entry agent (SocialMediaWriter)
        response = agency.get_completion(
            "Write a short LinkedIn post about why consistency is key in branding.",
            yield_messages=False
        )
        print("Response received from SocialMediaWriter:")
        print(response)
        
        # Check if response contains expected content
        if "consistency" in str(response).lower():
            print("\n[SUCCESS] Writer generated relevant content.")
        else:
            print("\n[WARNING] Response might not be relevant.")

    except Exception as e:
        print(f"\n[ERROR] Failed to run agency: {e}")

if __name__ == "__main__":
    test_social_media_writer()
