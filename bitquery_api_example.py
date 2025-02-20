import os
import sys
import json
import requests

API_URL = "https://streaming.bitquery.io/eap"

GRAPHQL_QUERY = """
query {
    Solana(dataset: archive) {
        DEXTradeByTokens(
            orderBy: { descendingByField: "Block_Timefield" },
            where: {
                Trade: {
                    Currency: { MintAddress: { is: "6D7NaB2xsLd7cauWu1wKk6KBsJohJmP2qZH9GEfVi5Ui" } },
                    Side: { Currency: { MintAddress: { is: "So11111111111111111111111111111111111111112" } } },
                    PriceAsymmetry: { lt: 0.1 }
                }
            },
            limit: { count: 3 }
        ) {
            Block {
                Timefield: Time(interval: { in: minutes, count: 1 })
            }
            volume: sum(of: Trade_Amount)
            Trade {
                high: Price(maximum: Trade_Price)
                low: Price(minimum: Trade_Price)
                open: Price(minimum: Block_Slot)
                close: Price(maximum: Block_Slot)
            }
            count
        }
    }
}
"""

def fetch_bitquery_data(api_token : str):
    """
    Fetches data from the Bitquery API using a GraphQL query.

    Args:
        api_token: The API token for authentication.

    Returns:
        dict: The JSON response from the API.
    """
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_token}"
    }

    payload = {
        "query": GRAPHQL_QUERY,
    }

    try:
        response = requests.post(API_URL, json=payload, headers=headers)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        sys.stderr.write(f"Error during API request: {e}\n")
        sys.exit(1)

    return response.json()

def main():
    api_token = os.environ.get("BITQUERY_API_TOKEN")
    if not api_token:
        sys.stderr.write("Error: BITQUERY_API_TOKEN environment variable is not set.\n")
        sys.exit(1)

    data = fetch_bitquery_data(api_token)

    with open("response.json", "w") as outfile:
        json.dump(data, outfile, indent=4)

if __name__ == "__main__":
    main()
