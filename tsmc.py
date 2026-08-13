import re
from datetime import datetime

import requests
from bs4 import BeautifulSoup


URL = "https://finance.yahoo.com/quote/2330.TW"


def get_tsmc_price() -> tuple[float, str]:
    """Return latest TSMC price and timestamp.

    Returns:
        (price, fetched_at_iso)
    """
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
        )
    }

    resp = requests.get(URL, headers=headers, timeout=10)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")

    # Primary: look for fin-streamer with data-field regularMarketPrice
    tag = soup.find("fin-streamer", {"data-field": "regularMarketPrice"})
    price_text = None

    if tag and tag.text:
        price_text = tag.text.strip()

    # Fallback: try regex on the page to find raw price in embedded JSON
    if not price_text:
        m = re.search(r'"regularMarketPrice":\{"raw":([0-9]+\.?[0-9]*)', resp.text)
        if m:
            price_text = m.group(1)

    if not price_text:
        raise RuntimeError("Could not find TSMC price on page")

    # normalize and convert
    price_text = price_text.replace(",", "")
    price = float(price_text)

    fetched_at = datetime.utcnow().isoformat() + "Z"
    return price, fetched_at


if __name__ == "__main__":
    try:
        price, at = get_tsmc_price()
        print(f"TSMC (2330.TW) price: {price} (fetched at {at})")
    except Exception as e:
        print("Error fetching TSMC price:", e)
