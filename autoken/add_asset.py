# Example: Adding assets
import json
import base64
from algosdk import account
from algosdk.v2client import algod
from algosdk.future import transaction

# These are the credentials for the sandbox replace with your local nodes or api if necessary 
def add_asset(private_key, address,):
    algod_address = "http://localhost:4001"
    algod_token = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
    algod_client = algod.AlgodClient(algod_token, algod_address)
    
    fee_per_byte = 0
    first_valid_round = 17365622
    last_valid_round = 17366621
    genesis_hash = "SGO1GKSzyE7IEPItTxCByw9x8FmnrCDexi9/cOUJOiI="
    receiver = address  # the sender is the reciever
    amount = 0  # to add asset, set amount to 0

    index = 22089866  # identifying index ID of the asset in this case Algoneer!

    # create the asset accept transaction
    sp = transaction.SuggestedParams(fee_per_byte, first_valid_round, last_valid_round, genesis_hash)
    txn = transaction.AssetTransferTxn(address, sp, receiver, amount, index)

    # sign the transaction
    signed_txn = txn.sign(private_key)
    txid = algod_client.send_transaction(signed_txn)
    print("Adding Asset: {}".format(txid))
    # wait for confirmation 
    try:
        confirmed_txn = wait_for_confirmation(algod_client, txid, 4)  
    except Exception as err:
        print(err)
        return

    #print("Transaction information: {}".format(json.dumps(confirmed_txn, indent=4)))
    #print("Decoded note: {}".format(base64.b64decode(confirmed_txn["txn"]["txn"]["note"]).decode()))
    print("Transaction info: {}".format(confirmed_txn["txn"]["txn"]))   # Prints tx info minus the sig
    account_info = algod_client.account_info(address)
    print("Account balance: {} microAlgos".format(account_info.get('amount')) + "\n")

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
# Input the private key and the address of the account adding the asset
add_asset('private_key', 'public_key')