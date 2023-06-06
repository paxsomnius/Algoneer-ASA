import os
import json
import time
import secrets
import uuid
import logging
import database_methods as db # pylint: disable=import-error
from algosdk.v2client import indexer
from algosdk.v2client import algod
from algosdk import transaction

def algod_client():
    """
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
    """
    indexer_address = "https://mainnet-algorand.api.purestake.io/idx2"
    indexer_token = keys.algod_token()[0] # Import your api key here
    headers = {
    "X-API-Key": indexer_token,
    }
    indexer_clients = indexer.IndexerClient(indexer_token, indexer_address, headers)
    return indexer_clients

class Lotto_Algo:
    """
    This class is used to create a ALGO lotto game on the Algorand blockchain.
    """
    def __init__(self,lottery_vars) -> None:
        self.lotto = lottery_vars
        self.folder = os.path.dirname(os.path.abspath(__file__))
        logging.basicConfig(filename=f'{self.folder}/global_lotto_errors.log', format='%(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S', encoding='utf-8', level=logging.ERROR)


    def balance(self) -> int:
        """
        Returns the account balance for the lotto account in algos
        """
        lotto_account_info = algod_client().account_info(self.lotto.lotto_address)
        lotto_balance = int(lotto_account_info.get("amount"))
        return lotto_balance

    def in_algo(self,_x_) -> int:
        """
        Function that converts float to algos
        """
        return int(_x_/1000000)


    def check_account_for_prize_payout(self):
        """
        Check the self.lotto account for prize payout
        This Game is: 10 testnet algo pot @ 1 algo per tx
        If the account has paid a prize returns a tuple containing: has_paid_out=True, last_payout_round("str")
        If the account has not paid a prize returns a tuple containing: has_paid_out=False, last_payout_round("")
        """
        print("Checking algo lotto account for prize payout...")
        payouts = []
        last_payout_round = ""
        if self.lotto.asa_id is None:
            tx_type = "pay"
        else:
            tx_type = "axfer"
        limit = None
        next_token = ""
        first_loop = True

        while next_token is not None:
            if first_loop is True:
                payout_check = indexer_client().search_transactions(limit=limit, txn_type=tx_type, min_amount=self.lotto.min_prize_amount, max_amount=self.lotto.max_prize_amount, address=self.lotto.lotto_address, address_role = "sender")
            else:
                payout_check = indexer_client().search_transactions(limit=limit, txn_type=tx_type, min_amount=self.lotto.min_prize_amount, max_amount=self.lotto.max_prize_amount, address=self.lotto.lotto_address, address_role = "sender", next=next_token)
            
            payouts += payout_check.get('transactions')
            next_token = payout_check.get('next_token')
            first_loop = False

        if len(payouts) > 0:
            payout_rounds_list = []
            has_paid_out = True
            for tx in payouts:
                payout_rounds_list.append(tx.get("confirmed-round"))
            print(f"This self.Lotto account has paid out the specified prize amount in these rounds: {payout_rounds_list}")
            last_payout_round = payout_rounds_list[0]
            print(f"End of function returning: {has_paid_out, last_payout_round}")
            return has_paid_out, last_payout_round
        has_paid_out = False
        print(f"This self.lotto account has not paid out the specified prize amount, returning:{has_paid_out,last_payout_round}")
        return has_paid_out, last_payout_round

    def transaction_count(self,last_payout_round):
        """
        Count the number of valid tx's into the self.lotto account after the last payout round\n
        :param self.lotto.min_bet_amount: Minimum tx value in microalgos
        :param self.lotto.max_bet_amount: Maximum tx value in microalgos
        :param self.lotto.self.lotto_address: self.Lotto account address
        :param last_payout_round: Last payout round
        :param self.lotto.asa_id: Optional self.lotto.asa_id
        :return: List of eligible accounts
        """
        valid_transaction_account_list = []
        min_amt = self.lotto.min_bet_amount
        max_amt = self.lotto.max_bet_amount
        print("Counting Transactions")
        print(min_amt, max_amt)
        limit = 10000
        if last_payout_round is not None:
            min_round = str(int(last_payout_round) + 1)
            print(f"Last payout round is not None, searching for transactions from last payout round: {last_payout_round}\n")
        else:
            min_round = self.lotto.lotto_account_operating_algo_transfer_round
            print(f"Last payout round is None, searching for transactions from initial operating algo transfer round.({self.lotto.lotto_account_operating_algo_transfer_round})\n")
        if self.lotto.asa_id is not None:
            txn_type = "axfer"
        else:
            txn_type = "pay"
        eligible_tx_list = []
        next_token = ""
        first_loop = True
        while next_token is not None:
            if first_loop is True:
                lotto_address_transaction_search = indexer_client().search_transactions(limit=limit, txn_type=txn_type, min_round=min_round, max_round=None, asset_id=self.lotto.asa_id, min_amount=min_amt, max_amount=max_amt, address=self.lotto.lotto_address, address_role = "receiver")
            else:
                lotto_address_transaction_search = indexer_client().search_transactions(limit=limit, next_page=next_token, txn_type=txn_type, min_round=min_round, max_round=None, asset_id=self.lotto.asa_id, min_amount=min_amt, max_amount=max_amt, address=self.lotto.lotto_address, address_role = "receiver")
            eligible_tx_list += lotto_address_transaction_search.get('transactions')
            next_token = lotto_address_transaction_search.get('next_token')
            first_loop = False
        for tx in eligible_tx_list:
            valid_transaction_account_list.append(tx.get("sender"))
        if len(valid_transaction_account_list) > self.lotto.max_valid_tx_list_length:
            return
        print(f"Valid transaction sending account list length: {len(valid_transaction_account_list)}\n")
        print(f"Valid transaction sending account List:\n {valid_transaction_account_list}\n")
        valid_transaction_account_list.reverse()
        print(f"Reversed list, first past the post:\n {valid_transaction_account_list}\n")
        return valid_transaction_account_list

    def illegal_tx_search(self,last_payout_round, s_type):
        """
        Search for the ineligible transactions into the self.lotto account from the last payout round, exclude the initial tx
        This Game is: 10 testnet algo pot @ 1 algo per tx
        :warning: There is a possible attack vector where an attacker could send 1m min
        :param bet_amount: The amount of Algos that are required to be paid into the self.lotto account to be eligible for the prize
        :param self.lotto.self.lotto_address: The self.lotto account address
        :param self.lotto.self.lotto_account_operating_algo_transfer_round: The round that the initial Algos were transferred to the self.lotto account
        :param last_payout_round: The round that the last prize was paid out
        :param self.lotto.asa_id: The asa id of the self.lotto token
        :return: Returns a dictionary of illegal accounts public keys and the amount of Algos that were paid into the self.lotto account in microalgos
        """
        if s_type == "under":
            print("\nSearching for illegal transactions under the bet amount\n")
        elif s_type == "over":
            print("\nSearching for illegal transactions over the bet amount\n")
        illegal_transaction_account_dict_over = {}
        illegal_transaction_account_dict_under = {}
        # Index to search for returns based on various search types (ie, under, over or late)
        limit = 10000
        # Finds bets which are under limit
        if s_type == "under":
            txn_type = "pay"
            min_amt = self.lotto.min_illegal_tx_amount  # In microalgos
            max_amt = self.lotto.bet_amount # In microalgos
            if last_payout_round is not None:
                min_round = str(int(last_payout_round))
            else:
                min_round = self.lotto.lotto_account_operating_algo_transfer_round

            illegal_tx_list = []
            next_token = str()
            first_loop = True
            indexer_client().search_transactions(limit=limit, next_page=next_token, txn_type=txn_type, min_round=min_round, max_round=None, asset_id=self.lotto.asa_id, min_amount=min_amt, max_amount=max_amt, address=self.lotto.lotto_address, address_role = "receiver")
            while next_token is not None:
                if first_loop is True:
                    illegal_tx_search_under = indexer_client().search_transactions(limit=limit, txn_type=txn_type, min_round=min_round, max_round=None, asset_id=self.lotto.asa_id, min_amount=min_amt, max_amount=max_amt, address=self.lotto.lotto_address, address_role = "receiver")
                else:
                    illegal_tx_search_under = indexer_client().search_transactions(limit=limit, next_page=next_token, txn_type=txn_type, min_round=min_round, max_round=None, asset_id=self.lotto.asa_id, min_amount=min_amt, max_amount=max_amt, address=self.lotto.lotto_address, address_role = "receiver")

                illegal_tx_list += illegal_tx_search_under.get('transactions')
                next_token = illegal_tx_search_under.get('next_token')
                first_loop = False
            for tx in illegal_tx_list:
                illegal_transaction_account_dict_under[tx.get("sender")] = tx.get('payment-transaction').get("amount")
            if self.lotto.lotto_address in illegal_transaction_account_dict_under:
                del illegal_transaction_account_dict_under[self.lotto.lotto_address]
            print(f"Illegal tx under Dict:{json.dumps(illegal_transaction_account_dict_under, indent=4)}\n")
            if len(illegal_transaction_account_dict_under) == 0 or len(illegal_transaction_account_dict_under) > self.lotto.max_illegal_tx_list_length:
                print("No illegal transactions found under the limit or the max illegal tx amount is exceeded")
                illegal_transaction_account_dict_under = None
                return illegal_transaction_account_dict_under
            print(f"Found {len(illegal_transaction_account_dict_under)} illegal transactions under the limit")
            return illegal_transaction_account_dict_under

        # Finds bets which are over limit
        else:
            min_amt = self.lotto.bet_amount # In microalgos
            max_amt = self.lotto.max_illegal_tx_amount
            txn_type = "pay"
            if last_payout_round is not None:
                min_round = str(int(last_payout_round))
            else:
                min_round = self.lotto.lotto_account_operating_algo_transfer_round

            illegal_tx_list = list()
            next_token = str()
            first_loop = True

            while next_token is not None:
                if first_loop is True:
                    illegal_tx_search_over = indexer_client().search_transactions(limit=limit, txn_type=txn_type, min_round=min_round, max_round=None, asset_id=self.lotto.asa_id, min_amount=min_amt, max_amount=max_amt, address=self.lotto.lotto_address, address_role = "receiver")
                else:
                    illegal_tx_search_over = indexer_client().search_transactions(limit=limit, next_page=next_token, txn_type=txn_type, min_round=min_round, max_round=None, asset_id=self.lotto.asa_id, min_amount=min_amt, max_amount=max_amt, address=self.lotto.lotto_address, address_role = "receiver")

                illegal_tx_list += illegal_tx_search_over.get('transactions')
                next_token = illegal_tx_search_over.get('next_token')
                first_loop = False
            for tx in illegal_tx_list:
                illegal_transaction_account_dict_over[tx.get("sender")] = tx.get('payment-transaction').get("amount")
            if self.lotto.lotto_address in illegal_transaction_account_dict_over:
                del illegal_transaction_account_dict_over[self.lotto.lotto_address]
            print(f"Illegal tx over Dict:{json.dumps(illegal_transaction_account_dict_over, indent=4)}")
            if len(illegal_transaction_account_dict_over) == 0 or len(illegal_transaction_account_dict_over) > self.lotto.max_illegal_tx_list_length:
                print("No illegal transactions found over the limit or the max illegal tx amount is exceeded")
                illegal_transaction_account_dict_over = None
                return illegal_transaction_account_dict_over
            print(f"Found {len(illegal_transaction_account_dict_over)} illegal transactions over the limit")
            return illegal_transaction_account_dict_over


    def send_prize(self,winning_address):
        """
        Send's Prize to winner - fees
            - prize payout((-2k ma for condolence tx)*(amount of bets needed for prize payout))
        This Game is: 10 testnet algo pot @ 1 algo per tx
        :param self.lotto_account: The self.lotto account address
        :param winning_address: The winning address
        :param prize_amount: The prize amount
        :param self.lotto.asa_id: The asa id of the prize ASA
        """
        tx_uuid = str(uuid.uuid4()) #uuid + monotonic counter necessary to keep transactions unique
        mono_ns = str(time.monotonic_ns())
        amount = self.lotto.prize_amount  # amount of asset to transfer
        index = self.lotto.asa_id  # ID of the asset to trasfer
        note = f"You won the Algoneer lotto! {str(self.in_algo(self.lotto.prize_amount))} Algo UUID: {tx_uuid} | {mono_ns}"
        sp = algod_client().suggested_params()
        tx = transaction.PaymentTxn(self.lotto.lotto_address, sp, winning_address, amount, note=note)
        signed_txn = tx.sign(self.lotto.lotto_account_private)
        txid = algod_client().send_transaction(signed_txn)
        try:
            db.add_prize_txn(self.lotto.game_id,self.lotto.game_id,txid,winning_address,amount)
        except Exception as e:
            logging.error("Error sending prize txn: %s", e)
            return
            

    def end_game(self,eligible_player_accounts):
        """
        This function runs when the end game conditions are met it takes the list of eligible players picks a winner then sends the prize to the winner and sends a note to the losers.
        This game is: 1 testnet algo bets @ 10 testnet algo pot
        :param eligible_player_accounts: The list of eligible player accounts in the draw for the prize
        :param prize_amount: The prize amount
        :param self.lotto_account: The self.lotto account address
        :param self.lotto_account_private: The self.lotto account private key
        :param network: The node type to use
        :param self.lotto.asa_id: The asa id of the wagered ASA
        ToDo: Add random notes
        """
        winner = secrets.choice(eligible_player_accounts)
        eligible_player_accounts.remove(winner)
        print("The winner is: ", winner)
        print("The prize is: ", self.lotto.prize_amount)
        print("Sending the losers a condolence note, rip")
        for loser in eligible_player_accounts:
            self.losing_bet_note_to_player(loser)
        print("Sending the winner their prize!!!")
        self.send_prize(winner)

    def bet_overflow_return_to_sender(self,rebate_address):
        """
        This function will return the overflow bet to it's sending address.
        This game is: 1 testnet algo bets @ 10 testnet algo pot
        :param return_fee: 1000 MA fee to cover the return tx fee
        :param self.lotto_account: The self.lotto account address
        :param rebate_address: The address to send the rebate to
        :param bet_amount: The bet amount
        :param network: The node type to use
        :param self.lotto.asa_id: The asa id of the wagered ASA
        """
        print(f"Sending overflow bet back to sender: {rebate_address}")
        tx_uuid = str(uuid.uuid4()) #uuid + monotonic counter necessary to keep transactions unique
        mono_ns = str(time.monotonic_ns())
        return_fee = 2000
        amount = self.lotto.bet_amount - return_fee  # amount of asset to transfer
        index = self.lotto.asa_id  # ID of the asset to trasfer
        note = f"Your bet was too late to the party! {str(self.in_algo(self.lotto.bet_amount))} UUID: {tx_uuid} | {mono_ns}"
        sp = algod_client().suggested_params()
        tx = transaction.PaymentTxn(self.lotto.lotto_address, sp, rebate_address, amount, note=note)
        signed_txn = tx.sign(self.lotto.lotto_account_private)
        txid = algod_client().send_transaction(signed_txn)
        try:
            db.add_overflow_txn(self.lotto.game_id,self.lotto.game_id,txid,rebate_address,amount)
        except Exception as e:
            logging.error("Error sending overflow txn: %s", e)
            return

    def rebate_illegal_bets(self,illegal_transaction_dict):
        """
        This function will return the incorrect bet amount to the sender, using a passed dict of ineligible accounts : tx_amount
        This game is: 1 testnet algo bets 10 algo pot
        :param self.lotto_account: The self.lotto account address
        :param self.lotto_account_private: The self.lotto account private key
        :param ineligible_bet_accounts: The dict of ineligible accounts and their bet amounts
        :param network: The node type to use
        :param self.lotto.asa_id: The asa id of the wagered ASA
        ToDo -
        Add ASA fee calculator to determine the return fee based on the ASA price
        """
        tx_uuid = str(uuid.uuid4())
        mono_ns = str(time.monotonic_ns())
        rebate_fee = 300000 # In microalgos
        ineligible_bet_accounts = illegal_transaction_dict
        for acc,tx_amount in ineligible_bet_accounts.items():
            if tx_amount < rebate_fee:
                ineligible_bet_accounts[acc] = 0
            else:
                tx_amount = tx_amount - rebate_fee
                ineligible_bet_accounts[acc] = tx_amount
        note = f"Your bet was incorrect here is your refund minus the return fee! {str(self.in_algo(tx_amount))} Algo UUID: {tx_uuid} | {mono_ns}"
        sp = algod_client().suggested_params()
        for pubk,taxed_tx_amt in ineligible_bet_accounts.items():
            print(f"\nRebating an illegal bet to the sender minus fee for the return\nSender: {pubk}\nRebate Amount: {taxed_tx_amt}")
            tx = transaction.PaymentTxn(self.lotto.lotto_address, sp, pubk, taxed_tx_amt, note=note)
            signed_txn = tx.sign(self.lotto.lotto_account_private)
            txid = algod_client().send_transaction(signed_txn)
            try:
                db.add_illegal_txn(self.lotto.game_id,self.lotto.game_id,txid,pubk,taxed_tx_amt)
            except Exception as e:
                logging.error("Error sending illegal txn: %s", e)
                return

    def losing_bet_note_to_player(self,losing_address):
        """
        This function will send a note to an eligible player informing that they lost the bet
        This game is: 1 testnet algo bets
        :param self.lotto_account: The self.lotto account address
        :param self.lotto_account_private: The self.lotto account private key
        :param losing_address: The address to send the note to
        :param bet_amount: The bet amount
        :param network: The node type to use
        """
        tx_uuid = str(uuid.uuid4()) #uuid + monotonic counter necessary to keep transactions unique
        mono_ns = str(time.monotonic_ns())
        amount = 0
        note = f"Hi, your bet of: {str(self.in_algo(self.lotto.bet_amount))} Algo was unsuccessful, please try again! UUID: {tx_uuid} | {mono_ns}"
        sp = algod_client().suggested_params()
        tx = transaction.PaymentTxn(self.lotto.lotto_address, sp, losing_address, amount, note=note.encode())
        signed_txn = tx.sign(self.lotto.lotto_account_private)
        txid = algod_client().send_transaction(signed_txn)
        try:
            db.add_losing_txn(self.lotto.game_id,self.lotto.game_id,txid,losing_address)
        except Exception as e:
            logging.error("Error sending condolence txn: %s", e)
            return

    def fee_collector(self):
        """
        This function will collect the fees from the self.lotto account
        :logic - Calculate the total amount of fees taken during end game conditions and send to the buyback account
        """
        tx_uuid = str(uuid.uuid4())
        mono_ns = str(time.monotonic_ns())
        excess_fees = int(self.balance() - self.lotto.starting_balance)
        print(f"Excess fees are: {excess_fees}")
        if excess_fees < 100000 or excess_fees - 5000 == self.lotto.prize_amount:
            print("No excess fees to collect")
            return
        amount = excess_fees - 5000
        note = "Fee Collection" + " " + "UUID:" + tx_uuid + " | " + mono_ns
        sp = algod_client().suggested_params()
        tx = transaction.PaymentTxn(self.lotto.lotto_address, sp, self.lotto.reswap_address, amount, note=note.encode())
        signed_txn = tx.sign(self.lotto.lotto_account_private)
        txid = algod_client().send_transaction(signed_txn)
        try:
            db.add_fee_txn(self.lotto.game_id,self.lotto.game_id,txid,amount)
        except Exception as e:
            logging.error("Error sending fee txn: %s", e)
            print("Error sending fee txn: %s", e)
            return
        print(f"Excess Fees collected and sent to the buyback account: {self.lotto.reswap_address}")

    def check_account(self):
        """
        This function will check the self.lotto account for the end game conditions.
        Change the self.lotto obj to change the lottery type
        """
        check = self.check_account_for_prize_payout()
        if check[0] is True:
            last_payout_round = check[1]
            print(f"Last Payout Round:{last_payout_round}")
            eligible_player_accounts = self.transaction_count(last_payout_round)
            if len(eligible_player_accounts) == 0:
                print("Checking\nNo bets\n\n")
            elif len(eligible_player_accounts) < self.lotto.amount_of_bets_required:
                print("Checking\nNot enough bets to end game.\n\n")
            elif len(eligible_player_accounts) == self.lotto.amount_of_bets_required:
                s_type = "over"
                illegal_tx_over = self.illegal_tx_search(last_payout_round, s_type)
                if illegal_tx_over is not None:
                    self.rebate_illegal_bets(illegal_tx_over)
                s_type = "under"
                illegal_tx_under = self.illegal_tx_search(last_payout_round, s_type)
                if illegal_tx_under is not None:
                    self.rebate_illegal_bets(illegal_tx_under)
                self.end_game(eligible_player_accounts)
                time.sleep(10)
                self.fee_collector()
            elif len(eligible_player_accounts) > self.lotto.amount_of_bets_required:
                ineligible_player_accounts = eligible_player_accounts[10:]
                eligible_player_accounts = eligible_player_accounts[:10]
                for rebate_address in ineligible_player_accounts:
                    self.bet_overflow_return_to_sender(rebate_address)
                s_type = "over"
                illegal_tx_over = self.illegal_tx_search(last_payout_round, s_type)
                if illegal_tx_over is not None:
                    self.rebate_illegal_bets(illegal_tx_over)
                s_type = "under"
                illegal_tx_under = self.illegal_tx_search(last_payout_round, s_type)
                if illegal_tx_under is not None:
                    self.rebate_illegal_bets(illegal_tx_under)
                self.end_game(eligible_player_accounts)
                time.sleep(10)
                self.fee_collector()
            
        else:
            last_payout_round = None
            eligible_player_accounts = self.transaction_count(last_payout_round)
            if len(eligible_player_accounts) == 0:
                print("Checking\nNo bets")
            elif len(eligible_player_accounts) < self.lotto.amount_of_bets_required:
                print("Checking\nNot enough bets to end game.")
            elif len(eligible_player_accounts) == self.lotto.amount_of_bets_required:
                s_type = "over"
                illegal_tx_over = self.illegal_tx_search(last_payout_round, s_type)
                if illegal_tx_over is not None:
                    self.rebate_illegal_bets(illegal_tx_over)
                s_type = "under"
                illegal_tx_under = self.illegal_tx_search(last_payout_round, s_type)
                if illegal_tx_under is not None:
                    self.rebate_illegal_bets(illegal_tx_under)
                self.end_game(eligible_player_accounts)
                time.sleep(10)
                self.fee_collector()
            elif len(eligible_player_accounts) > self.lotto.amount_of_bets_required:
                ineligible_player_accounts = eligible_player_accounts[self.lotto.amount_of_bets_required:]
                eligible_player_accounts = eligible_player_accounts[:self.lotto.amount_of_bets_required]
                for rebate_address in ineligible_player_accounts:
                    self.bet_overflow_return_to_sender(rebate_address)
                s_type = "over"
                illegal_tx_over = self.illegal_tx_search(last_payout_round, s_type)
                if illegal_tx_over is not None:
                    self.rebate_illegal_bets(illegal_tx_over)
                s_type = "under"
                illegal_tx_under = self.illegal_tx_search(last_payout_round, s_type)
                if illegal_tx_under is not None:
                    self.rebate_illegal_bets(illegal_tx_under)
                self.end_game(eligible_player_accounts)
                time.sleep(10)
                self.fee_collector()


class Lotto_ASA:
    """
    This class is used to create a ASA lotto game on the Algorand blockchain.
    """
    def __init__(self,lottery_vars) -> None:
        self.lotto = lottery_vars
        self.folder = os.path.dirname(os.path.abspath(__file__))
        logging.basicConfig(filename=f'{self.folder}_lotto_errors.log', format='%(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S', encoding='utf-8', level=logging.ERROR)

    def balance(self) -> int:
        """
        Returns the account balance for the lotto account in algos
        """
        lotto_account_info = algod_client().account_info(self.lotto.lotto_address)
        print(lotto_account_info)
        lotto_balance = int(lotto_account_info.get("amount"))/1000000
        return lotto_balance

    def asa_balance(self) -> int:
        """
        Returns the asa balance for the lotto account in microunits
        """
        lotto_account_info = algod_client().account_asset_info(self.lotto.lotto_address, self.lotto.asa_id)
        lotto_balance = lotto_account_info.get("asset-holding").get("amount")
        print(f"ASA Balance: {lotto_balance}")
        return lotto_balance

    def in_microunits(self,_x_) -> int:
        """
        function that converts float to a given assets microunits
        """
        return int(_x_*(10 ** self.lotto.asset_micro_unit))

    def in_asset_units(self,_x_) -> int:
        """
        function that converts a float given assets microunits to units
        """
        return int(_x_/(10 ** self.lotto.asset_micro_unit))
    
    def reset_lastround(self):
        """
        Resets the last payout round to lotto start round
        """
        filepath = f"{self.folder}/{self.lotto.game_id}_last_payout.json"
        last_payout_round = [self.lotto.lotto_account_operating_algo_transfer_round]
        if not os.path.exists(filepath):
            open_type = 'x'
        else:
            open_type = 'w'
        with open(filepath, open_type) as lst_rnd:
            data = last_payout_round
            json.dump(data, lst_rnd, indent=4)
            lst_rnd.close()

    def check_account_for_asa_prize_payout(self):
        """
        Determines the last payout round
        If the account has paid a prize returns a tuple containing: has_paid_out=True, last_payout_round("str")
        If the account has not paid a prize returns a tuple containing: has_paid_out=False, last_payout_round("")
        """
        print("Checking payout_tx for prize payout...")
        filepath = f"{self.folder}/{self.lotto.game_id}_last_payout.json"
        if not os.path.exists(filepath):
            print("No payout_tx file found, creating...")
            self.reset_lastround()
        with open(filepath, "r") as file:
            lst_rnd = json.load(file)
        last_payout_round = lst_rnd[0]
        return last_payout_round

    def transaction_count(self,last_payout_round):
        """
        Count the number of valid tx's into the self.lotto account after the last payout round\n
        :param self.lotto.min_bet_amount: Minimum tx value in microalgos
        :param self.lotto.max_bet_amount: Maximum tx value in microalgos
        :param self.lotto.self.lotto_address: self.Lotto account address
        :param last_payout_round: Last payout round
        :param self.lotto.asa_id: Optional self.lotto.asa_id
        :return: List of eligible accounts
        """
        valid_transaction_account_list = []
        min_amt = self.lotto.min_bet_amount
        max_amt = self.lotto.max_bet_amount
        print("Counting Transactions")
        print(min_amt, max_amt)
        limit = 10000
        min_round = str(int(last_payout_round) + 1)
        print(f"Searching for transactions from last payout round: {last_payout_round}\n")
        if self.lotto.asa_id is not None:
            txn_type = "axfer"
        else:
            txn_type = "pay"
        eligible_tx_list = []
        next_token = ""
        first_loop = True
        while next_token is not None:
            if first_loop is True:
                lotto_address_transaction_search = indexer_client().search_transactions(limit=limit, txn_type=txn_type, min_round=min_round, max_round=None, asset_id=self.lotto.asa_id, min_amount=min_amt, max_amount=max_amt, address=self.lotto.lotto_address, address_role = "receiver")
            else:
                lotto_address_transaction_search = indexer_client().search_transactions(limit=limit, next_page=next_token, txn_type=txn_type, min_round=min_round, max_round=None, asset_id=self.lotto.asa_id, min_amount=min_amt, max_amount=max_amt, address=self.lotto.lotto_address, address_role = "receiver")
            eligible_tx_list += lotto_address_transaction_search.get('transactions')
            next_token = lotto_address_transaction_search.get('next_token')
            first_loop = False
        for tx in eligible_tx_list:
            valid_transaction_account_list.append(tx.get("sender"))
        if len(valid_transaction_account_list) > self.lotto.max_valid_tx_list_length:
            return
        print(f"Valid transaction sending account list length: {len(valid_transaction_account_list)}\n")
        print(f"Valid transaction sending account list:\n {valid_transaction_account_list}\n")
        valid_transaction_account_list.reverse()
        print(f"Reversed list, first past the post:\n {valid_transaction_account_list}\n")
        return valid_transaction_account_list

    def illegal_tx_search(self,last_payout_round, s_type):
        """
        Search for the ineligible transactions into the self.lotto account from the last payout round, exclude the initial tx
        This Game is: 10 testnet algo pot @ 1 algo per tx
        :warning: There is a possible attack vector where an attacker could send 1m min
        :param bet_amount: The amount of Algos that are required to be paid into the self.lotto account to be eligible for the prize
        :param self.lotto.self.lotto_address: The self.lotto account address
        :param self.lotto.self.lotto_account_operating_algo_transfer_round: The round that the initial Algos were transferred to the self.lotto account
        :param last_payout_round: The round that the last prize was paid out
        :param self.lotto.asa_id: The asa id of the self.lotto token
        :return: Returns a dictionary of illegal accounts public keys and the amount of Algos that were paid into the self.lotto account in microalgos
        """
        if s_type == "under":
            print("\nSearching for illegal transactions under the bet amount\n")
        elif s_type == "over":
            print("\nSearching for illegal transactions over the bet amount\n")
        illegal_transaction_account_dict_over = {}
        illegal_transaction_account_dict_under = {}
        # Index to search for returns based on various search types (ie, under, over or late)
        limit = 10000
        # Finds bets which are under limit
        if s_type == "under":
            txn_type = "axfer"
            min_amt = self.lotto.min_illegal_tx_amount  # In microalgos
            max_amt = self.lotto.bet_amount # In microalgos
            if last_payout_round is not None:
                min_round = str(int(last_payout_round))
            else:
                min_round = self.lotto.lotto_account_operating_algo_transfer_round

            illegal_tx_list = []
            next_token = ""
            first_loop = True
            indexer_client().search_transactions(limit=limit, next_page=next_token, txn_type=txn_type, min_round=min_round, max_round=None, asset_id=self.lotto.asa_id, min_amount=min_amt, max_amount=max_amt, address=self.lotto.lotto_address, address_role = "receiver")
            while next_token is not None:
                if first_loop is True:
                    illegal_tx_search_under = indexer_client().search_transactions(limit=limit, txn_type=txn_type, min_round=min_round, max_round=None, asset_id=self.lotto.asa_id, min_amount=min_amt, max_amount=max_amt, address=self.lotto.lotto_address, address_role = "receiver")
                else:
                    illegal_tx_search_under = indexer_client().search_transactions(limit=limit, next_page=next_token, txn_type=txn_type, min_round=min_round, max_round=None, asset_id=self.lotto.asa_id, min_amount=min_amt, max_amount=max_amt, address=self.lotto.lotto_address, address_role = "receiver")

                illegal_tx_list += illegal_tx_search_under.get('transactions')
                next_token = illegal_tx_search_under.get('next_token')
                first_loop = False
            for tx in illegal_tx_list:
                illegal_transaction_account_dict_under[tx.get("sender")] = tx.get("asset-transfer-transaction").get("amount")
            if self.lotto.lotto_address in illegal_transaction_account_dict_under:
                del illegal_transaction_account_dict_under[self.lotto.lotto_address]
            print(f"Illegal tx under Dict:{json.dumps(illegal_transaction_account_dict_under, indent=4)}\n")
            if len(illegal_transaction_account_dict_under) == 0 or len(illegal_transaction_account_dict_under) > self.lotto.max_illegal_tx_list_length:
                print("No illegal transactions found under the limit or the max illegal tx amount is exceeded")
                illegal_transaction_account_dict_under = None
                return illegal_transaction_account_dict_under
            print(f"Found {len(illegal_transaction_account_dict_under)} illegal transactions under the limit")
            return illegal_transaction_account_dict_under

        # Finds bets which are over limit
        else:
            min_amt = self.lotto.bet_amount # In microalgos
            max_amt = self.lotto.max_illegal_tx_amount
            txn_type = "axfer"
            if last_payout_round is not None:
                min_round = str(int(last_payout_round))
            else:
                min_round = self.lotto.lotto_account_operating_algo_transfer_round

            illegal_tx_list = list()
            next_token = str()
            first_loop = True

            while next_token is not None:
                if first_loop is True:
                    illegal_tx_search_over = indexer_client().search_transactions(limit=limit, txn_type=txn_type, min_round=min_round, max_round=None, asset_id=self.lotto.asa_id, min_amount=min_amt, max_amount=max_amt, address=self.lotto.lotto_address, address_role = "receiver")
                else:
                    illegal_tx_search_over = indexer_client().search_transactions(limit=limit, next_page=next_token, txn_type=txn_type, min_round=min_round, max_round=None, asset_id=self.lotto.asa_id, min_amount=min_amt, max_amount=max_amt, address=self.lotto.lotto_address, address_role = "receiver")

                illegal_tx_list += illegal_tx_search_over.get('transactions')
                next_token = illegal_tx_search_over.get('next_token')
                first_loop = False
            for tx in illegal_tx_list:
                illegal_transaction_account_dict_over[tx.get("sender")] = tx.get("asset-transfer-transaction").get("amount")
            if self.lotto.lotto_address in illegal_transaction_account_dict_over:
                del illegal_transaction_account_dict_over[self.lotto.lotto_address]
            print(f"Illegal tx over Dict:{json.dumps(illegal_transaction_account_dict_over, indent=4)}")
            if len(illegal_transaction_account_dict_over) == 0 or len(illegal_transaction_account_dict_over) > self.lotto.max_illegal_tx_list_length:
                print("No illegal transactions found over the limit or the max illegal tx amount is exceeded")
                illegal_transaction_account_dict_over = None
                return illegal_transaction_account_dict_over
            print(f"Found {len(illegal_transaction_account_dict_over)} illegal transactions over the limit")
            return illegal_transaction_account_dict_over


    def send_prize(self,winning_address):
        """
        Send's Prize to winner - fees
            - prize payout((-2k ma for condolence tx)*(amount of bets needed for prize payout))
        This Game is: 10 testnet algo pot @ 1 algo per tx
        :param self.lotto_account: The self.lotto account address
        :param winning_address: The winning address
        :param prize_amount: The prize amount
        :param self.lotto.asa_id: The asa id of the prize ASA
        """
        txfilepath = f"{self.folder}/{self.lotto.game_id}_last_payout_tx.json"
        rndfilepath = f"{self.folder}/{self.lotto.game_id}_last_payout.json"
        tx_uuid = str(uuid.uuid4()) #uuid + monotonic counter necessary to keep transactions unique
        mono_ns = str(time.monotonic_ns())
        amount = self.lotto.prize_amount  # amount of asset to transfer
        index = self.lotto.asa_id  # ID of the asset to trasfer
        note = f"You won the ASA lotto! {str(self.in_asset_units(self.lotto.prize_amount))} {self.lotto.asset_unit_name} UUID: {tx_uuid} | {mono_ns}"
        sp = algod_client().suggested_params()
        tx = transaction.AssetTransferTxn(self.lotto.lotto_address, sp, winning_address, amount, index, note=note)
        signed_txn = tx.sign(self.lotto.lotto_account_private)
        submit = algod_client().send_transaction(signed_txn)
        try:
            with open(txfilepath, 'w') as lst_rnd:
                data = [submit]
                json.dump(data, lst_rnd, indent=4)
                lst_rnd.close()
            db.add_prize_txn(self.lotto.game_id,self.lotto.game_id,data[0],winning_address,self.lotto.prize_amount,self.lotto.asa_id,self.lotto.asset_unit_name)
            time.sleep(10)
            print("Saving last payout round")
            with open(txfilepath, 'r') as lst_rnd:
                data = json.load(lst_rnd)
                rnd = [indexer_client().transaction(data[0])['transaction']['confirmed-round']]
                lst_rnd.close()
            with open(rndfilepath, 'w') as lst_rnd:
                json.dump(rnd, lst_rnd, indent=4)
                lst_rnd.close()
        except Exception as e:
            logging.error("Error sending prize: %s", e)
            print("Error sending prize: ", e)
            return



    def end_game(self,eligible_player_accounts):
        """
        This function runs when the end game conditions are met it takes the list of eligible players picks a winner then sends the prize to the winner and sends a note to the losers.
        This game is: 1 testnet algo bets @ 10 testnet algo pot
        :param eligible_player_accounts: The list of eligible player accounts in the draw for the prize
        :param prize_amount: The prize amount
        :param self.lotto_account: The self.lotto account address
        :param self.lotto_account_private: The self.lotto account private key
        :param network: The node type to use
        :param self.lotto.asa_id: The asa id of the wagered ASA
        ToDo: Add random notes
        """
        winner = secrets.choice(eligible_player_accounts)
        eligible_player_accounts.remove(winner)
        print("The winner is: ", winner)
        print("The prize is: ", self.lotto.prize_amount)
        print("Sending the losers a condolence note, rip")
        for loser in eligible_player_accounts:
            self.losing_bet_note_to_player(loser)
        print("Sending the winner their prize!!!")
        self.send_prize(winner)

    def bet_overflow_return_to_sender(self,rebate_address):
        """
        This function will return the overflow bet to it's sending address.
        This game is: 1 testnet algo bets @ 10 testnet algo pot
        :param return_fee: 1000 MA fee to cover the return tx fee
        :param self.lotto_account: The self.lotto account address
        :param rebate_address: The address to send the rebate to
        :param bet_amount: The bet amount
        :param network: The node type to use
        :param self.lotto.asa_id: The asa id of the wagered ASA
        """
        print(f"Sending overflow bet back to sender: {rebate_address}")
        tx_uuid = str(uuid.uuid4()) #uuid + monotonic counter necessary to keep transactions unique
        mono_ns = str(time.monotonic_ns())
        return_fee = self.lotto.asa_ovflo_return_fee
        amount = self.lotto.bet_amount - return_fee  # amount of asset to transfer
        if amount < 0:
            print ("After fees amount is less than 0, not sending overflow")
            return
        index = self.lotto.asa_id  # ID of the asset to trasfer
        note = f"Your bet was too late to the party! {str(self.in_asset_units(self.lotto.bet_amount))}UUID: {tx_uuid} | {mono_ns}"
        sp = algod_client().suggested_params()
        tx = transaction.AssetTransferTxn(self.lotto.lotto_address, sp, rebate_address, amount, index, note=note)
        signed_txn = tx.sign(self.lotto.lotto_account_private)
        txid = algod_client().send_transaction(signed_txn)
        try:
            db.add_overflow_txn(self.lotto.game_id,self.lotto.game_id,txid,rebate_address,amount,index,self.lotto.asset_unit_name)
        except Exception as e:
            logging.error("Error sending overflow: %s", e)
            print("Error sending overflow: ", e)

    def rebate_illegal_bets(self,illegal_transaction_dict):
        """
        This function will return the incorrect bet amount to the sender, using a passed dict of ineligible accounts : tx_amount
        :param self.lotto_account: The self.lotto account address
        :param self.lotto_account_private: The self.lotto account private key
        :param ineligible_bet_accounts: The dict of ineligible accounts and their bet amounts
        :param network: The node type to use
        :param self.lotto.asa_id: The asa id of the wagered ASA
        """
        tx_uuid = str(uuid.uuid4()) #uuid + monotonic counter necessary to keep transactions unique
        mono_ns = str(time.monotonic_ns())
        rebate_fee = self.lotto.asa_rebate_fee # In microalgos
        ineligible_bet_accounts = illegal_transaction_dict
        index = self.lotto.asa_id
        for acc,tx_amount in ineligible_bet_accounts.items():
            if tx_amount < rebate_fee:
                ineligible_bet_accounts[acc] = 0
            else:
                tx_amount = tx_amount - rebate_fee
                ineligible_bet_accounts[acc] = tx_amount
        note = f"Your bet was incorrect here is your refund minus the return cost! {str(self.in_asset_units(tx_amount))} {self.lotto.asset_unit_name} UUID: {tx_uuid} | {mono_ns}"
        sp = algod_client().suggested_params()
        for pubk,taxed_tx_amt in ineligible_bet_accounts.items():
            print(f"Rebating an illegal bet to the sender minus fee for the return\nSender: {pubk}\nRebate Amount: {taxed_tx_amt}")
            tx = transaction.AssetTransferTxn(self.lotto.lotto_address, sp, pubk, taxed_tx_amt, index, note=note)
            signed_txn = tx.sign(self.lotto.lotto_account_private)
            txid = algod_client().send_transaction(signed_txn)
            try:
                db.add_illegal_txn(self.lotto.game_id,self.lotto.game_id,txid,pubk,taxed_tx_amt,index,self.lotto.asset_unit_name)
            except Exception as e:
                logging.error("Error sending illegal bet rebate: %s", e)
                print("Error sending illegal bet rebate: %s", e)

    def losing_bet_note_to_player(self,losing_address):
        """
        This function will send a note to an eligible player informing that they lost the bet
        This game is: 1 testnet algo bets
        :param self.lotto_account: The self.lotto account address
        :param self.lotto_account_private: The self.lotto account private key
        :param losing_address: The address to send the note to
        :param bet_amount: The bet amount
        :param network: The node type to use
        """
        tx_uuid = str(uuid.uuid4()) #uuid + monotonic counter necessary to keep transactions unique
        mono_ns = str(time.monotonic_ns())
        amount = 0
        note = f"Hi, your bet of: {str(self.in_asset_units(self.lotto.bet_amount))} | {self.lotto.asset_unit_name} was unsuccessful, please try again! UUID: {tx_uuid} | {mono_ns}"
        sp = algod_client().suggested_params()
        tx = transaction.PaymentTxn(self.lotto.lotto_address, sp, losing_address, amount, note=note.encode())
        signed_txn = tx.sign(self.lotto.lotto_account_private)
        txid = algod_client().send_transaction(signed_txn)
        try:
            print("Saving losing bet note transaction to db")
            db.add_losing_txn(self.lotto.game_id,self.lotto.game_id,txid,losing_address)
        except Exception as e:
            logging.error("Error sending condolence bet note: %s", e)
            print("Error sending condolence bet note: %s", e)

    def fee_collector(self):
        """
        This function will collect the fees from the lotto account
        :logic - Calculate the total amount of fees taken during end game conditions and send to the buyback account
        """
        tx_uuid = str(uuid.uuid4()) #uuid + monotonic counter necessary to keep transactions unique
        mono_ns = str(time.monotonic_ns())
        excess_fees = self.asa_balance()
        print(f"Excess fees are: {excess_fees}")
        if excess_fees < self.lotto.excess_fee_floor or excess_fees == self.lotto.prize_amount:
            return print("No excess fees to collect")
        amount = excess_fees
        _id_= self.lotto.asa_id
        note = f"Fee Collection UUID: {tx_uuid} | {mono_ns}"
        sp = algod_client().suggested_params()
        tx = transaction.AssetTransferTxn(self.lotto.lotto_address, sp, self.lotto.reswap_address, amount, _id_, note=note.encode())
        signed_txn = tx.sign(self.lotto.lotto_account_private)
        txid = algod_client().send_transaction(signed_txn)
        try:
            db.add_fee_txn(self.lotto.game_id,self.lotto.game_id,txid, amount,_id_,self.lotto.asset_unit_name)
            print(f"Fees collected and sent to the buyback account: {self.lotto.reswap_address}")
        except Exception as e:
            logging.error("Error sending fee collection: %s", e)
            print("Error sending fee collection: %s", e)
        

    def check_account(self):
        """
        This function will check the self.lotto account for the end game conditions.
        Change the self.lotto obj to change the lottery type
        """
        check = self.check_account_for_asa_prize_payout()
        last_payout_round = check
        print(f"Last Payout Round:{last_payout_round}")
        eligible_player_accounts = self.transaction_count(last_payout_round)
        if len(eligible_player_accounts) == 0:
            print("Checking\nNo bets\n\n")
        elif len(eligible_player_accounts) < self.lotto.amount_of_bets_required:
            print("Checking\nNot enough bets to end game.\n\n")
        elif len(eligible_player_accounts) == self.lotto.amount_of_bets_required:
            s_type = "over"
            illegal_tx_over = self.illegal_tx_search(last_payout_round, s_type)
            if illegal_tx_over is not None:
                self.rebate_illegal_bets(illegal_tx_over)
            s_type = "under"
            illegal_tx_under = self.illegal_tx_search(last_payout_round, s_type)
            if illegal_tx_under is not None:
                self.rebate_illegal_bets(illegal_tx_under)
            self.end_game(eligible_player_accounts)
            self.fee_collector()
        elif len(eligible_player_accounts) > self.lotto.amount_of_bets_required:
            ineligible_player_accounts = eligible_player_accounts[self.lotto.amount_of_bets_required:]
            eligible_player_accounts = eligible_player_accounts[:self.lotto.amount_of_bets_required]
            for rebate_address in ineligible_player_accounts:
                self.bet_overflow_return_to_sender(rebate_address)
            s_type = "over"
            illegal_tx_over = self.illegal_tx_search(last_payout_round, s_type)
            if illegal_tx_over is not None:
                self.rebate_illegal_bets(illegal_tx_over)
            s_type = "under"
            illegal_tx_under = self.illegal_tx_search(last_payout_round, s_type)
            if illegal_tx_under is not None:
                self.rebate_illegal_bets(illegal_tx_under)
            self.end_game(eligible_player_accounts)
            self.fee_collector()
