import json
import time
import logging
import uuid
import os
from datetime import datetime
import database_methods as db # pylint: disable=import-error
from algosdk.v2client import indexer
from algosdk.v2client import algod
from algosdk import transaction
from tinyman.v2.client import TinymanV2MainnetClient
from tinyman.v2.client import TinymanV2TestnetClient



def algod_client():
    """
    Algod Client
    """
    algod_address = "https://mainnet-algorand.api.purestake.io/ps2"
    algod_token = keys.algod_token()[0] # Import your api key here
    headers = {
    "X-API-Key": algod_token,
    }
    algod_clients = algod.AlgodClient(algod_token, algod_address, headers)
    return algod_clients

def indexer_client():
    """
    Indexer Client
    """
    indexer_address = "https://mainnet-algorand.api.purestake.io/idx2"
    indexer_token = keys.algod_token()[0] # Import your api key here
    headers = {
    "X-API-Key": indexer_token,
    }
    indexer_clients = indexer.IndexerClient(indexer_token, indexer_address, headers)
    return indexer_clients 


class Reswap_Bot:
    """
    Reswap bot, controls the reSwap_account and handels the AGNR buybacks and maintenance fees, and ASA Lottery account algo top ups
    """
    def __init__(self):
        self.folder = os.path.dirname(os.path.abspath(__file__))
        logging.basicConfig(filename=f'{self.folder}/reswap_errors.log', format='%(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S', encoding='utf-8', level=logging.ERROR)
        self.reswap_min_algo_balance = 10000000 # 10 Algo buffer
        self.min_value_asa_swap = 1000000 # 1 Algo
        self.reswap_address = keys.reswap_account()[0]
        self.reswap_prikey = keys.reswap_account()[1]
        self.network = "mainnet"
        self.transact = True
        self.reserve = keys.bank_account()[0]
        self.agnr_id = 305992851 # --> int
        self.burn = keys.burn_account()[0]
        self.maintenance_fee_percent = .1 # Decimal Form 0.01 = 1%
        self.database = "mainnet_reswap"
        self.agnr_buy_records = "mainnet_reswap_agnr_buybacks"
        self.agnr_burn_records = "mainnet_reswap_agnr_burns"
        self.asa_swap_records = "mainnet_reswap_asa_swaps"
        self.maintenance_fee_records = "mainnet_reswap_maintenance_fees"
        self.monitored_addresses = keys.control_monitored_addr_list()
        self.asa_lotto_addresses = keys.asa_lotto_addr_list()
        self.control = keys.control_account()
    
    def record_maker(self,file_name,data):
        """
        Save transaction info to json file
        Set up list for use in our records
        """
        logging.info("ReswapBot Called Record Maker")
        timenow = datetime.utcnow().strftime('utc_%Y_%m_%d_%H_%M_%S') + '_txids'
        records_dict = [{timenow: [data]}]
        filepath = f'{self.folder}/{file_name}.json'
        if not os.path.exists(filepath):
            open_type = 'w+'
        else:
            open_type = 'r+'
        with open(filepath, open_type, encoding="utf-8") as buyback_doc:
            if open_type == 'r+':
                buyback_list = json.load(buyback_doc)
                buyback_doc.seek(0)
                buyback_list.append(records_dict[0])
            else:
                buyback_list = records_dict
            json.dump(buyback_list, buyback_doc, indent=4)
            buyback_doc.close()

    def min_algo_balance(self) -> int:
        """
        Gets min req algo balance of reSwap_account
        """
        logging.info("Bot called !min_algo_balance! func")
        lotto_account_info = algod_client().account_info(self.reswap_address)
        lotto_balance = int(lotto_account_info.get("min-balance"))
        return lotto_balance

    def algo_balance(self) -> int:
        """
        Gets algo balance of reSwap_account, subtracts min req amount and returns algo balance in microalgo
        """
        logging.info("Bot called: algo_balance func")
        account_info = algod_client().account_info(self.reswap_address)
        lotto_balance = int(account_info.get("amount"))
        min_balance = int(account_info.get("min-balance"))
        lotto_balance = lotto_balance - min_balance
        return lotto_balance

    def asa_list(self)  -> dict:
        """
        Gets list of asa's opted in to reSwap_account and their balances
        returns dict of asa's and balances
        ToDo:
            Block agnr from list
        """
        logging.info("Bot called: asa_list func")
        asa_dict = {}
        asset_search = algod_client().account_info(self.reswap_address)
        for asa in asset_search.get('assets'):
            if asa.get('asset-id') != self.agnr_id:
                asa_dict[asa.get('asset-id')] = asa.get('amount')
        print(f"Fetching all assets held by the reswap bot: {asa_dict}")
        return asa_dict

    def swap_algo(self) -> None:
        """
        Checks if reSwap_account has min algo balance, and  swaps the difference + 1 algo for AGNR
        """
        logging.info("Bot called: buy_agnr func")
        print("Checking if reSwap_account has enough Algo to swap for AGNR")
        if self.algo_balance() <= self.reswap_min_algo_balance:
            print("Not enough Algo in reSwap_account, aborting swap")
            return
        if self.algo_balance() > self.reswap_min_algo_balance:
            print("May be enough Algo in reSwap_account, adding 10 algo buffer to swap")
            difference = self.algo_balance() - self.reswap_min_algo_balance
            if difference > 10000000:
                amt = difference
                tinyman_client = TinymanV2MainnetClient(algod_client=algod_client(), user_address=self.reswap_address)
                if self.network == "testnet":
                    tinyman_client = TinymanV2TestnetClient(algod_client=algod_client(), user_address=self.reswap_address)
                Agnr = tinyman_client.fetch_asset(self.agnr_id)
                Algo = tinyman_client.fetch_asset(0)
                pool = tinyman_client.fetch_pool(Agnr, Algo)
                quote = pool.fetch_fixed_input_swap_quote(Algo(amt), slippage=0.01)
                print(f'Purchasing {quote.amount_out_with_slippage.amount / 1000} AGNR for {quote.amount_in.amount / 1_000_000} '
                    f'Algo.\n')
                txn = pool.prepare_swap_transactions_from_quote(quote)
                txn.sign_with_private_key(self.reswap_address, self.reswap_prikey)
                if self.transact is True:
                    try:
                        print("Transact is true, buying agnr! submitting TX!\n")
                        result = tinyman_client.submit(txn, wait=False).get('txid')
                        db.add_reswap_agnr_buyback(self.database,result,amt)
                    except Exception as _e_:
                        logging.error("Error: %s", _e_)
                        print(f"Error: {_e_}")
                        return
                else:
                    note = "Buy agnr TX Created, but transact was set to false!"
                    self.record_maker(self.agnr_buy_records,note)
                    print("Transact was false, but the TX was successfully created!\n")
            else:
                print("Difference was less than 10 algo, aborting swap")
                return


    def swap_asa(self) -> None:
        """
        Swap asa balance to algo
        Takes a dict containing all asa's and their balance the reswap account holds\n loops through it and skips thos who have 0 balance\n those whos balance is not enough to cover the swap cost (~1 algo equivalant)\n after filtering it will only swap to algo the assets with a correct balance.\n
        """
        logging.info("Bot called: swap_asa func")
        print("Checking if value of asa's are worth swapping to algo")
        asa_dict = self.asa_list()
        recievd = 0
        for _k_,_v_ in asa_dict.items():
            a_id = _k_
            a_bal = _v_
            if a_bal == 0:
                print("No balance of this asset, skipping")
                continue
            if a_bal > 0:
                min_val = self.min_value_asa_swap
                min_amt = self.asa_min_calc(min_val,a_id)
                if a_bal < min_amt:
                    print("Not enough of this asset to swap, skipping")
                    continue
                if a_bal > min_amt:
                    tinyman_client = TinymanV2MainnetClient(algod_client=algod_client(), user_address=self.reswap_address)
                    if self.network == "testnet":
                        tinyman_client = TinymanV2TestnetClient(algod_client=algod_client(), user_address=self.reswap_address)
                    # Fetch our two assets of interest
                    ASA = tinyman_client.fetch_asset(a_id)
                    Algo = tinyman_client.fetch_asset(0)
                    # Fetch pool
                    pool = tinyman_client.fetch_pool(Algo,ASA)
                    # Get quote to swap our buy amount into AGNR
                    quote = pool.fetch_fixed_input_swap_quote(ASA(a_bal), slippage=0.01)
                    print(f'Swapping {quote.amount_out_with_slippage.amount} of ASA for {quote.amount_in.amount / 1_000_000} '
                        f'Algo.\n')
                    # Transact with Tinyman
                    txn = pool.prepare_swap_transactions_from_quote(quote)
                    txn.sign_with_private_key(self.reswap_address, self.reswap_prikey)
                    if self.transact is True:
                        try:
                            print("Transact is true, buying agnr! submitting TX!\n")
                            result = tinyman_client.submit(txn, wait=True).get('txid')
                            db.add_reswap_asa_swap_to_algo(self.database,result,a_bal,a_id)
                            recievd += 1
                        except Exception as _e_:
                            logging.error("Error: %s", _e_)
                            print("Error: %s", _e_)
                            return
                    else:
                        note = "Buy agnr TX Created, but transact was set to false!"
                        self.record_maker(self.asa_swap_records,note)
                        print("Transact was false, but the TX was successfully created!\n")
        if recievd > 0:
            print(f"Successfully swapped {recievd} assets to algo!")
            self.asa_lotto_operating_algo()
        
    def maintenance_fee(self) -> None:
        """
        Function takes a percentage of excess AGNR balance as maintenance fees, and sends it to the AGNR reserve account
        percentage = percentage of excess agnr balance to be sent to reserve account, in decimal form .01 = 1%
        Call before Burn
        """
        logging.info("Bot called: maintenance_cost func")
        asset_id = self.agnr_id
        asset_search = algod_client().account_asset_info(self.reswap_address,asset_id)
        asset_balance = asset_search['asset-holding']['amount']
        print(f"AGNR Balance: {asset_balance}")
        maintenance_fee = int(asset_balance * self.maintenance_fee_percent)
        print(f"Sending maintenance fee to reserve account: {maintenance_fee} AGNR")
        tx_uuid = str(uuid.uuid4()) #uuid + monotonic counter necessary to keep transactions unique
        mono_ns = str(time.monotonic_ns())
        amount = maintenance_fee # amount of asset to transfer
        index = asset_id # ID of the asset to transfer
        note = f"Maintenance fee in AGNR UUID:  {tx_uuid} | {mono_ns}"
        sp = algod_client().suggested_params()
        tx = transaction.AssetTransferTxn(self.reswap_address, sp, self.reserve, amount, index, note=note)
        signed_txn = tx.sign(self.reswap_prikey)
        submit_tx = algod_client().send_transaction(signed_txn)
        try:
            db.add_reswap_maintenance_fee(self.database,submit_tx,maintenance_fee,self.reserve,index)
        except Exception() as _e_:
            logging.error("Error: %s", _e_)
            print("Error: %s", _e_)
            return

    def burn_agnr(self) -> None:
        """
        Burns remaining AGNR Balance
        """
        logging.info("Bot called: burn_agnr func")
        print("Commencing the burn!")
        asset_id = self.agnr_id
        asset_search = algod_client().account_asset_info(self.reswap_address,asset_id)
        asset_balance = asset_search['asset-holding']['amount']
        print(f"AGNR reswap Balance: {asset_balance}")
        if asset_balance == 0:
            print("No AGNR balance, skipping burn")
            return
        tx_uuid = str(uuid.uuid4()) #uuid + monotonic counter necessary to keep transactions unique
        mono_ns = str(time.monotonic_ns())
        amount = asset_balance # amount of asset to transfer
        index = asset_id # ID of the asset to transfer
        note = f"AGNR Burn UUID:  {tx_uuid}  | {mono_ns}"
        sp = algod_client().suggested_params()
        tx = transaction.AssetTransferTxn(self.reswap_address, sp, self.burn, amount, index, note=note)
        signed_txn = tx.sign(self.reswap_prikey)
        submit_tx = algod_client().send_transaction(signed_txn)
        print("AGNR is burning!")
        try:
            db.add_reswap_agnr_burn(self.database,submit_tx,amount)
        except Exception() as _e_:
            logging.error("Error: %s", _e_)
            print("Error: %s", _e_)
            return

    def control_algo_check(self) -> None:
        """
        Checks reswap/ASA Lotto's algo balance and tops up from control if below critical buffer balance
        """
        logging.info("Bot called: control_account func")
        address_list = self.monitored_addresses
        print("Control is checking algo reserves for critical buffer balance....")
        for address in address_list:
            lotto_account_info = algod_client().account_info(address)
            lotto_balance = int(lotto_account_info.get("amount"))
            min_balance = int(lotto_account_info.get("min-balance")) + 2000000
            sub_balance = lotto_balance - min_balance
            print(f"Monitored account: {address} has a balance of: {lotto_balance} microAlgos")
            print(f"Monitored account: {address} has a minimum balance of: {min_balance} microAlgos")
            if sub_balance <= 0:
                logging.info("Monitored account is below critical balance, topping up! %s", address)
                tx_uuid = str(uuid.uuid4())
                mono_ns = str(time.monotonic_ns())
                amount = sub_balance + min_balance
                note = f"Monitored account top up UUID:  {tx_uuid} | {mono_ns}"
                sp = algod_client().suggested_params()
                tx = transaction.PaymentTxn(self.control[0], sp, address, amount, note=note)
                signed_txn = tx.sign(self.control[1])
                submit_tx = algod_client().send_transaction(signed_txn)
                try:
                    db.add_reswap_reserve_topup(self.database,submit_tx,amount,address)
                except Exception() as _e_:
                    logging.error("Error: %s", _e_)
                    print("Error: %s", _e_)
                    return
            
    
    def asa_lotto_operating_algo(self) -> None:
        """
        Checks all ASA Lotto's algo balance and tops up from swapped algo if below starting balance
        """
        logging.info("Bot called: asa_lotto_operating_algo func")
        print("Checking all live ASA Lotteries algo reserves....")
        address_list = self.asa_lotto_addresses
        starting_balance = self.reswap_min_algo_balance
        reswap_balance = self.algo_balance()
        debt_balance_list = []
        debt_address_list = []
        for address in address_list:
            lotto_account_info = algod_client().account_info(address)
            lotto_balance = int(lotto_account_info.get("amount"))
            min_balance = int(lotto_account_info.get("min-balance")) + starting_balance
            sub_balance = min_balance - lotto_balance
            print(f"ASA Lotto account: {address} has a debt of: {sub_balance} microAlgos")
            if sub_balance > 100000:
                print(f"ASA Lotto account: {address} is below operating balance adding to debt list...")
                debt_address_list.append(address)
                debt_balance_list.append(sub_balance)
        total_debt = sum(debt_balance_list) + 1000
        print(f"Total debt: {total_debt}")
        print(f"Reswap balance: {reswap_balance}")
        if total_debt < reswap_balance:
            for _k_,_v_ in zip(debt_address_list,debt_balance_list):
                logging.info("ASA Lotto account is below operating balance, topping up! %s", _k_)
                print(f"ASA Lotto account: {_k_} is below operating balance, topping up!")
                tx_uuid = str(uuid.uuid4())
                mono_ns = str(time.monotonic_ns())
                amount = _v_
                note = f"ASA Lotto account: {_k_} top up UUID:  {tx_uuid} | {mono_ns}"
                sp = algod_client().suggested_params()
                tx = transaction.PaymentTxn(self.reswap_address, sp, _k_, amount, note=note)
                signed_txn = tx.sign(self.reswap_prikey)
                submit_tx = algod_client().send_transaction(signed_txn)
                try:
                    db.add_reswap_lotto_topup(self.database,submit_tx,amount,_k_)
                except Exception() as _e_:
                    logging.error("Error: %s", _e_)
                    print("Error: %s", _e_)
                    return

    def asa_min_calc(self, minalgo, asa_id) -> int:
        """
        Calculates minimum amount of ASA required for swap, from ASA to Algo
        """
        logging.info("Bot called: asa_min_calc func")
        algo = minalgo
        algod_address = f"https://{self.network}-algorand.api.purestake.io/ps2"
        algod_token = keys.algod_token()[0]
        headers = {
            "X-API-Key": algod_token,
        }
        algod_clients = algod.AlgodClient(algod_token, algod_address, headers)
        client = TinymanV2MainnetClient(algod_client=algod_clients)
        MLAH = client.fetch_asset(asa_id)
        ALGO = client.fetch_asset(0)
        pool = client.fetch_pool(MLAH, ALGO)
        quote = pool.fetch_fixed_input_swap_quote(amount_in=ALGO(algo), slippage=0.01, refresh=False)
        print(f"Pinging the tinyman, quote: {int(quote.amount_out.amount)}")
        try:
            return int(quote.amount_out.amount)
        except Exception() as _e_:
            logging.error("Bot error: %s", _e_)
            print("Bot error: ", _e_)
        