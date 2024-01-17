

import requests


url = "https://quote-api.jup.ag/v6/quote"


payload = {
    "inputMint": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
    "outputMint": "So11111111111111111111111111111111111111112",
    "amount": 1000
}
headers = {
  'Accept': 'application/json'
}

url = url + "?" + "&".join([f"{k}={v}" for k, v in payload.items()])

response = requests.get(url, headers=headers)


print(response.text)


