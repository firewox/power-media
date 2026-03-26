import json
import urllib.request
import sys

def get_ip_info():
    """
    Fetches the public IP and detailed network information from ipapi.co.
    """
    try:
        # Fetching from ipapi.co
        with urllib.request.urlopen("https://ipapi.co/json/", timeout=10) as response:
            if response.status == 200:
                data = json.loads(response.read().decode('utf-8'))
                
                # Format the output
                output = [
                    f"Public IP: {data.get('ip')}",
                    f"Country: {data.get('country_name')} ({data.get('country_code')})",
                    f"Region: {data.get('region')}",
                    f"City: {data.get('city')}",
                    f"ISP: {data.get('org')}",
                    f"ASN: {data.get('asn')}",
                    f"Timezone: {data.get('timezone')}"
                ]
                print("\n".join(output))
            else:
                print(f"Error: Received status code {response.status}")
    except Exception as e:
        # Fallback to a simpler service if ipapi.co fails
        try:
            with urllib.request.urlopen("https://api.ipify.org?format=json", timeout=5) as response:
                if response.status == 200:
                    data = json.loads(response.read().decode('utf-8'))
                    print(f"Public IP: {data.get('ip')}")
                    print("(Detailed info unavailable - ipapi.co failed)")
                else:
                    print(f"Error fetching IP: {e}")
        except Exception as e2:
            print(f"Error: Could not retrieve IP information. {e2}")

if __name__ == "__main__":
    get_ip_info()
