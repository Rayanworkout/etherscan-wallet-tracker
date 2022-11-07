import requests


def get_balance(address):
        
    data = requests.get("https://api.etherscan.io/api?module=account&action=balance"
                        f"&address={address}&tag=latest&apikey=8H1U3JF6KGZIJH2VBSF6QE96R73I13NTAF").json()
    
    if data["message"] == "NOTOK":
        return "Could not get Balance"
    
    return round(int(data['result']) / 10 ** 18, 3)


def get_all_transactions(address, qty=15):
    
    normal_tx_url = (f"/api?module=account&action=txlist&address={address}&startblock=0"
           f"&endblock=99999999&page=1&offset={qty}&sort=desc&apikey=8H1U3JF6KGZIJH2VBSF6QE96R73I13NTAF")
    
    internal_tx_url = (f"/api?module=account&action=txlistinternal&address={address}&startblock=0"
           f"&endblock=99999999&page=1&offset={qty}&sort=desc&apikey=8H1U3JF6KGZIJH2VBSF6QE96R73I13NTAF")
    
    normal_txs_response = requests.get("https://api.etherscan.io" + normal_tx_url).json()
    internal_tx_response = requests.get("https://api.etherscan.io" + internal_tx_url).json()
    
    
    if normal_txs_response["message"] == "NOTOK" or internal_tx_response["message"] == "NOTOK":
        return "error getting transactions for this account"
    
    data = dict()
        
    for tx in normal_txs_response["result"] + internal_tx_response["result"]:
        
        data[tx["hash"]] = {"hash": tx["hash"],
                            "from": tx["from"],
                            "to": tx["to"],
                            "value": round(int(tx["value"]) / 10 ** 18, 4),
                            "time": tx["timeStamp"],
                            "type": "normal" if tx["hash"] in [tx["hash"] for tx in normal_txs_response["result"]] else "internal",
                            "isError": tx["isError"],
                            "contractAddress": tx["contractAddress"] if tx["contractAddress"] else None}
    if not data:
        return "no transaction found for this account"
    
    return data

def telegram_messge(message):
    requests.get(f"https://api.telegram.org/bot1768068100:AAHVGEdeItHypLHBfqmMoqdqhX4KdgO08Gc/"
                 f"sendMessage?chat_id=901170303&text={message}")


def scrape_transaction_action():
    "https://etherscan.io/tx/0x986e0a39c0d45bd3558229206063662fbc111e03885f836a7f25585b3ca865e6"
    pass
