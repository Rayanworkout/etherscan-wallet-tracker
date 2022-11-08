import requests
import json

from web3 import Web3

contract_address = "0x617dee16b86534a5d792a4d7a62fb491b544111e"
methodID = "0xabcffc26"

def get_func_called(methodID):
    if methodID:
        return requests.get(f'https://raw.githubusercontent.com/ethereum-lists/4bytes/master/signatures/{methodID[2:10]}').text
    else:
        return "Not Found"
    
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


print((get_function_from_methodID(contract=contract_address, methodID=methodID)))