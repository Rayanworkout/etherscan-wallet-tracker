import json
import os
import time

from utils import get_all_transactions, get_balance, telegram_messge

from discord_webhook import DiscordEmbed, DiscordWebhook
    

# RENDRE MULTICHAIN

###################################################################################################

webhook = DiscordWebhook(
        url = 'https://discord.com/api/webhooks/1038669013863104572/6IEqXuZOh'
              'UHtrervvnaAx3WaLRR3rgfRqctqD2lTdN6wph2ZgvriftDPCXgrzj_NKIkp',
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
                    print("no new transaction")
                    
                elif result:
                    print(f"{len(result)} new transaction(s) found")
                    
                    for transaction in result:
                        
                        # convert timestamp to readable date
                        tx_date = time.strftime("%d/%m/%Y %H:%M:%S", time.localtime(int(transaction["timestamp"])))
                        
                        if transaction["isError"] == "0":
                            description = ( f"**Address Tag:** {folder.upper()}\n\n"
                                            f"**Hash:** {transaction['hash']}\n\n"
                                            f"**From:** {transaction['from']}\n\n"
                                            f"**To:** {transaction['to']}\n\n"
                                            f"**Value:** {transaction['value']} ETH\n\n"
                                            f"**Timestamp:** {tx_date}\n\n"
                                            f"**Type:** {transaction['type']}\n\n"
                                            f"**Contract Address:** {transaction['contractAddress']}")
                                                
                            embed = DiscordEmbed(title=tracked_account, description=description, color="1DA1F2",
                                                    url=f"https://etherscan.io/tx/{transaction['hash']}")
                            
                            embed.set_author(name="NEW TRANSACTION", description=f"Balance: {get_balance(tracked_account)} ETH")
                                                    
                            embed.set_timestamp()
                            
                            webhook.add_embed(embed)
                            webhook.execute()
            
            time.sleep(15)
    
    except Exception as err:
        telegram_messge(f"Error with wallet tracker bot: {err}")
        exit()