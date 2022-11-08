import requests

import json

from web3 import Web3

#############################################################################################################

def telegram_message(message):
    requests.get(f"https://api.telegram.org/bot1768068100:AAHVGEdeItHypLHBfqmMoqdqhX4KdgO08Gc/"
                 f"sendMessage?chat_id=901170303&text={message}")

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
                            "contractAddress": tx["contractAddress"] if tx["contractAddress"] else None,
                            "input": tx["input"] if tx["input"] else None}
    if not data:
        return "no transaction found for this account"
    
    return data

#############################################################################################################
   
def get_contract_abi(contract_address, write_to_file=False):
    """Get ABI of a contract and returns it to json format"""

    url = (f"https://api.etherscan.io/api?module=contract&action=getabi&address={contract_address}&"
           f"apikey=8H1U3JF6KGZIJH2VBSF6QE96R73I13NTAF")

    response = requests.get(url).json()
    abi = json.loads(response['result'])
    
    if write_to_file:
        with open(f'abi_{contract_address}.json', 'w') as f:
            json.dump(abi, f, indent=4)

    return abi


def get_all_methods_and_parameters(abi):
    w3 = Web3()
    data = dict()

    for entry in abi:
        if entry['type'] == 'function':
            function = entry['name'] + '(' + ','.join([i['type'] for i in entry['inputs']]) + ')'
            methodId = w3.sha3(text=function)[0:4].hex()
            data[methodId] = function

    return data


def find_function(data, hash):
    for key, value in data.items():
        if key == hash:
            return value
    return "Not found"

#############################################################################################################

def get_function_from_methodID(contract, methodID):
    """Trying to find the function name from the methodID
    first with an API call to 4bytes and if not found trying
    to compute it with contract ABI"""
    
    if methodID:
        api = requests.get(f'https://raw.githubusercontent.com/ethereum-lists/4bytes/master/signatures/{methodID}').text
        if api == "404: Not Found":
            abi = get_contract_abi(contract)
            data = get_all_methods_and_parameters(abi)
            
            return find_function(data, methodID)

        