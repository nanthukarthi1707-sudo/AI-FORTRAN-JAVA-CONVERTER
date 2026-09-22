import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=api_key)

models_to_test = [
    "gemini-3.1-flash-lite",
    "gemini-3.5-flash-lite",
    "gemini-3.5-flash",
    "gemini-3.6-flash",
    "gemini-3.7-flash",
    "gemini-3.8-flash",
]

print("========== MODEL TEST ==========")

for model in models_to_test:

    print(f"\nTesting: {model}")

    try:
        response = client.models.generate_content(
            model=model,
            contents="Reply with exactly: TEST SUCCESS"
        )

        print("SUCCESS!")
        print("Response:", response.text)
        print("\nWORKING MODEL:", model)
        break

    except Exception as e:

        error = str(e)

        if "503" in error:
            print("503 - temporarily unavailable")

        elif "404" in error:
            print("404 - model not available")

        elif "429" in error:
            print("429 - quota/rate limit")

        else:
            print("ERROR:", error)

print("\n========== TEST COMPLETE ==========")