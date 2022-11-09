import json
import os
import time

from utils import get_all_transactions, get_balance, telegram_message, get_function_from_methodID

from discord_webhook import DiscordEmbed, DiscordWebhook
    

###################################################################################################

test = "https://discord.com/api/webhooks/953362427884478484/XKStZT199JlRCrrwWBnQnPPd0HdvqQmixYxHGkeVJBNjDvhaGz_e--4JJvbFA35YazsR"
prod = "https://discord.com/api/webhooks/1038669013863104572/6IEqXuZOhUHtrervvnaAx3WaLRR3rgfRqctqD2lTdN6wph2ZgvriftDPCXgrzj_NKIkp"

webhook = DiscordWebhook(
        url = prod,
    username='WALLET TRACKER'
)

###################################################################################################

def check_address(address):
    data = get_all_transactions(address)
        
    if data not in ["error getting transactions for this account", "no transaction found for this account"]:
        for folder in os.listdir("tracked_accounts"):
            if f"{address}.json" in os.listdir(f"tracked_accounts/{folder}"):
                with open(f"tracked_accounts/{folder}/{address}.json", "r") as f:
                    old_data = json.load(f)
            
                with open(f"tracked_accounts/{folder}/{address}.json", "w") as f:
                    json.dump(data, f, indent=4)
            
                new_transactions = [data[tx] for tx in data if tx not in old_data]
                
                if not new_transactions:
                    return None 
                
                return new_transactions


if not os.path.isdir("tracked_accounts"):
    os.mkdir("tracked_accounts")
    
while True:
    
    try:
                
        if not os.listdir("tracked_accounts"):
            print("No accounts are being tracked right now ...")
            time.sleep(30)
        
        for folder in os.listdir("tracked_accounts"):
            
            for tracked_account in [file.replace(".json", "") for file in os.listdir(f"tracked_accounts/{folder}")]:
                
                print(">>> checking", tracked_account)
                
                result = check_address(tracked_account)
                
                if not result:
                    print("no new transaction\n")
                    
                elif result:
                    print(f"{len(result)} new transaction(s) found\n\n")
                    
                    for transaction in result:
                        
                        tx_date = time.strftime("%d/%m/%Y %H:%M:%S", time.localtime(int(transaction["time"])))
                        
                        if transaction["isError"] == "0":
                            
                            method = get_function_from_methodID(contract=transaction['to'], methodID=transaction["input"][:10])
                            
                            description = ( f"**Address Tag:** {folder.upper()}\n\n"
                                            f"**Hash:** {transaction['hash']}\n\n"
                                            f"**Method:** {method}\n\n"
                                            f"**From:** {transaction['from']}\n\n"
                                            f"**To:** {transaction['to']}\n\n"
                                            f"**Value:** {transaction['value']} ETH\n\n"
                                            f"**Timestamp:** {tx_date}\n\n"
                                            f"**Type:** {transaction['type']}\n\n")
                                                
                            embed = DiscordEmbed(title=tracked_account, description=description, color="1DA1F2",
                                                    url=f"https://etherscan.io/tx/{transaction['hash']}")
                            
                            embed.set_author(name=f"NEW TRANSACTION / Current Balance: {get_balance(tracked_account)} ETH")
                                                    
                            embed.set_timestamp()
                            
                            webhook.add_embed(embed)
                            webhook.execute()
                            print("Discord message sent")
            
            time.sleep(15)
    
    except Exception as err:
        telegram_message(f"Error with wallet tracker bot: {str(err)}")
    
    except json.JSONDecodeError:
        pass
