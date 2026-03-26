---
name: check-ip
description: This skill should be used when the user needs to check their public/outgoing IP address, location, or ISP information. It's particularly useful for debugging API connectivity issues (like WeChat Official Account 40007 errors), checking IP whitelists, or verifying network configuration.
---

# Check IP

## Overview

This skill provides a quick way to retrieve the public IP address and detailed network information (Country, Region, City, ISP, ASN) of the local machine. It uses reliable external services to ensure accurate outgoing IP detection.

## Use Cases

- **IP Whitelisting**: When a user needs to know their IP to add it to a service's whitelist (e.g., WeChat Official Account, AWS, Database).
- **Network Debugging**: Verifying if the traffic is routed through the expected ISP or VPN.
- **Geolocation**: Checking the physical location associated with the current network connection.

## Workflow

To retrieve IP information, run the provided Python script.

```bash
python .trae/skills/check-ip/scripts/get_ip_info.py
```

### Script Details: `scripts/get_ip_info.py`

- **Primary Source**: `https://ipapi.co/json/` (Detailed JSON info)
- **Fallback Source**: `https://api.ipify.org?format=json` (Simple IP only)
- **Output**: Formatted text including IP, Country, Region, City, ISP, ASN, and Timezone.

## Concrete Examples

### Example 1: User asks for their IP
User: "What is my public IP?"
Claude: [Invokes `check-ip` skill and runs the script] "Your public IP is 223.160.230.135, located in Guangzhou, China."

### Example 2: Debugging API errors
User: "I'm getting a 40007 invalid media_id error from WeChat API. Is it because of my IP?"
Claude: "While 40007 usually refers to invalid media_id, it's worth checking if your IP is whitelisted. Let me check your outgoing IP for you." [Invokes `check-ip` skill and runs the script]

## Resources

### scripts/
- `get_ip_info.py`: Python script using standard library `urllib` to fetch IP data.
