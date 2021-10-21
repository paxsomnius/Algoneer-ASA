import json
import base64
from algosdk import account, mnemonic
from algosdk.v2client import algod
from algosdk.future.transaction import AssetTransferTxn
from algosdk.future import transaction
import time


def generate_algorand_keypair():
    private_key, address = account.generate_account()
    print("My address: {}".format(address))
    print("My private key: {}".format(private_key))
    print("My passphrase: {}".format(mnemonic.from_private_key(private_key)))

# Write down your address, private key, and the passphrase for later usage
# generate_algorand_keypair() # Uncomment this line to use the keypair generator
# My address:
# My private key:
# My passphrase:

# These are the credentials for the sandbox replace with your local nodes or api if necessary 
def send_transactions(private_key, send_address):
    algod_address = "http://localhost:4001"
    algod_token = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
    algod_client = algod.AlgodClient(algod_token, algod_address)

    print("From: {}".format(send_address))
    account_info = algod_client.account_info(send_address)
    print("Balance: {} microAlgos".format(account_info.get('amount')))

    # build transaction
    fee = 1000
    first_valid_round = 17380481
    last_valid_round = 17381479
    gh = "SGO1GKSzyE7IEPItTxCByw9x8FmnrCDexi9/cOUJOiI="
    receiver = key
    amount = 1  # amount of assets to transfer
    index = 22089866  # ID of the asset

    # create the asset transfer transaction
    sp = transaction.SuggestedParams(fee, first_valid_round, last_valid_round, gh, gen=None, flat_fee=True)
    txn = AssetTransferTxn(send_address, sp, receiver, amount, index)

    # sign the transaction
    signed_txn = txn.sign(private_key)
    # sign the transaction
    signed_txn = txn.sign(private_key)
    txid = algod_client.send_transaction(signed_txn)
    print("TxId: {}".format(txid) + "\nSending Asset....")
    # wait for confirmation 
    try:
        confirmed_txn = wait_for_confirmation(algod_client, txid, 4)  
    except Exception as err:
        print(err)
        return

    #print("Transaction information: {}".format(json.dumps(confirmed_txn, indent=4))) #Prints All tx info including sig
    #print("Decoded note: {}".format(base64.b64decode(confirmed_txn["txn"]["txn"]["note"]).decode())) # Prints the Note field if specced
    print("Transaction info: {}".format(confirmed_txn["txn"]["txn"]))   # Prints tx info minus the sig

    account_info = algod_client.account_info(send_address)
    print("New Balance: {} microAlgos".format(account_info.get('amount')) + "\n")

# utility function for waiting on a transaction confirmation
def wait_for_confirmation(client, transaction_id, timeout):
    """
    Wait until the transaction is confirmed or rejected, or until 'timeout'
    number of rounds have passed.
    Args:
        transaction_id (str): the transaction to wait for
        timeout (int): maximum number of rounds to wait    
    Returns:
        dict: pending transaction information, or throws an error if the transaction
            is not confirmed or rejected in the next timeout rounds
    """
    start_round = client.status()["last-round"] + 1
    current_round = start_round

    while current_round < start_round + timeout:
        try:
            pending_txn = client.pending_transaction_info(transaction_id)
        except Exception:
            return 
        if pending_txn.get("confirmed-round", 0) > 0:
            return pending_txn
        elif pending_txn["pool-error"]:  
            raise Exception(
                'pool error: {}'.format(pending_txn["pool-error"]))
        client.status_after_block(current_round)                   
        current_round += 1
    raise Exception(
        'pending tx not found in timeout rounds, timeout value = : {}'.format(timeout))

# Replace private_key and send_address with your private key and send address
# Get Keys from .txt file into a list, Get a Key from key_list call the function and loop for evey key in the key_list 
key_list = []
with open('PATH/to/.txt/file/containing/keys', 'r') as file:
    for line in file:
        key_list.extend(line.split())
print("Imported Key's: {}".format(key_list) + "\n")
for key in key_list:
    key_from_list = key
    send_transactions('private_key', 'send_address')
