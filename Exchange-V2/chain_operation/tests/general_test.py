import requests
import json

url = "https://quote-api.jup.ag/v6/swap"

mode = "ExactIn"
left = "So11111111111111111111111111111111111111112"
right = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"
me = "APWPbTf6vYqLfeyCd3kYCbBSDtB36gtJY9tDsXNiZznu"

payload = json.dumps({
    "userPublicKey": me,
    "wrapAndUnwrapSol": True,
    "useSharedAccounts": True,
    "feeAccount": left if mode == "ExactIn" else right,
    "asLegacyTransaction": False,
    "restrictIntermediateTokens": True,
    "useTokenLedger": False,
    "dynamicComputeUnitLimit": True,
    "skipUserAccountsRpcCalls": True,
    "destinationTokenAccount": me,
    "quoteResponse": {
        "inputMint": right,
        "inAmount": "1000",
        "outputMint": left,
        "outAmount": "10007",
        "otherAmountThreshold": "9957",
        "swapMode": mode,
        "slippageBps": 50,
        "platformFee": None,
        "priceImpactPct": "0.002979504139971435417591379",
        "routePlan": [{
            "swapInfo": {
                "ammKey": "FoSDw2L5DmTuQTFe55gWPDXf88euaxAEKFre74CnvQbX",
                "label": "Meteora DLMM",
                "inputMint": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
                "outputMint": "So11111111111111111111111111111111111111112",
                "inAmount": "1000",
                "outAmount": "10164",
                "feeAmount": "1",
                "feeMint": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"
            },
            "percent": 100},
        ],
        "contextSlot": 242313031,
        "timeTaken": 0.004212803
    }
})
headers = {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
}

response = requests.request("POST", url, headers=headers, data=payload)

print(response.text)
