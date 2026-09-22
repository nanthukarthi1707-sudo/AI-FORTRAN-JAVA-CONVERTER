import os
import socket
from dotenv import load_dotenv
from google import genai

load_dotenv()

print("========== GEMINI DEBUG ==========")

# 1. Check API key
api_key = os.getenv("GEMINI_API_KEY")

if api_key:
    print("1. API key: FOUND")
else:
    print("1. API key: NOT FOUND")
    exit()

# 2. Check DNS
print("\n2. Checking Google DNS...")

try:
    ip = socket.gethostbyname("generativelanguage.googleapis.com")
    print("   DNS: OK")
    print("   IP:", ip)
except Exception as e:
    print("   DNS: FAILED")
    print("   Error:", e)
    exit()

# 3. Create client
print("\n3. Creating Gemini client...")

try:
    client = genai.Client(api_key=api_key)
    print("   Client: OK")
except Exception as e:
    print("   Client: FAILED")
    print("   Error:", e)
    exit()

# 4. List models
print("\n4. Checking model access...")

try:
    models = list(client.models.list())

    print("   Models API: OK")
    print("   Number of models:", len(models))

except Exception as e:
    print("   Models API: FAILED")
    print("   Error:", e)
    exit()

# 5. Test generation
print("\n5. Testing generation...")

try:
    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents="Reply with exactly: TEST SUCCESS"
    )

    print("   Generation: SUCCESS")
    print("   Response:", response.text)

except Exception as e:
    print("   Generation: FAILED")
    print("   Error type:", type(e).__name__)
    print("   Error:", e)

print("\n========== DEBUG COMPLETE ==========")