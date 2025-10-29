import requests

json_endpoint = (
    "https://sportsobama.com/domain.php"
)

response = requests.get(json_endpoint)

print("Status Code:", response.status_code)
print("Content-Type:", response.headers.get("Content-Type", "N/A"))
print("\n--- RESPONSE CONTENT ---\n")
print(response.text)
