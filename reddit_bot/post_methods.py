from algosdk.v2client import indexer
from algosdk.v2client import algod

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

#Indexer client
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


class AlgoLottoInfo:
    """
    This class gets relavant info about a lotto game
    """
    def __init__(self, lotto_address, initial_round, max_valid_tx, amt_bets_required,bet_amount, fixed_fee, prize_feee):
        self.lotto_address = lotto_address
        self.initial_round = initial_round
        self.max_valid_tx_list_length = max_valid_tx
        self.amt_bets_required = amt_bets_required
        self.bet_amount = bet_amount
        self.min_bet_amount = self.bet_amount - 1
        self.max_bet_amount = self.bet_amount + 1
        self.fixed_fee = fixed_fee
        self.prize_fee = prize_feee * self.amt_bets_required + fixed_fee
        self.prize_amount = (bet_amount * self.amt_bets_required) - self.prize_fee
        self.min_prize_amount = self.prize_amount - 1
        self.max_prize_amount = self.prize_amount + 1
        self.asa_id = None

    def balance(self) -> int:
        """
        Returns the account balance for the lotto account in algos
        """
        lotto_account_info = algod_client().account_info(self.lotto_address)
        lotto_balance = int(lotto_account_info.get("amount"))/1000000
        return lotto_balance
    def prize_amt(self) -> int:
        """
        Returns the prize amount for the lotto game
        """
        return self.prize_amount/1000000

    def check_account_for_prize_payout(self) -> str:
        """
        Check the lotto account for prize payout transactions\n
        """
        print("Checking lotto account for prize payout...")
        payouts = []
        last_payout_round = ""
        if self.asa_id is None:
            tx_type = "pay"
        else:
            tx_type = "axfer"
        limit = None
        next_token = str()
        first_loop = True

        while next_token is not None:
            if first_loop is True:
                payout_check = indexer_client().search_transactions(limit=limit, txn_type=tx_type, min_amount=self.min_prize_amount, max_amount=self.max_prize_amount, address=self.lotto_address, address_role = "sender")
            else:
                payout_check = indexer_client().search_transactions(limit=limit, txn_type=tx_type, min_amount=self.min_prize_amount, max_amount=self.max_prize_amount, address=self.lotto_address, address_role = "sender", next=next_token)
            
            payouts += payout_check.get('transactions')
            next_token = payout_check.get('next_token')
            first_loop = False

        if len(payouts) > 0:
            payout_rounds_list = []
            for tx in payouts:
                payout_rounds_list.append(tx.get("confirmed-round"))
            print(f"This Lotto account has paid out the specified prize amount in these rounds: {payout_rounds_list}")
            last_payout_round = payout_rounds_list[0]
            print(f"End of function returning: {last_payout_round}")
            return last_payout_round
        print(f"This lotto account has not paid out the specified prize amount, returning:{last_payout_round}")
        return last_payout_round is None

    def transaction_count(self) -> int:
        """
        Count the number of valid tx's into the lotto account after the last payout round\n
        :return: List of eligible accounts
        """
        last_payout_round = self.check_account_for_prize_payout()
        valid_transaction_account_list = []
        min_amt = self.min_bet_amount
        max_amt = self.max_bet_amount
        print("Counting Transactions")
        print(min_amt, max_amt)
        limit = None
        if last_payout_round is not None:
            min_round = str(int(last_payout_round) + 1)
            print(f"Last payout round is not None, searching for transactions from last payout round: {last_payout_round}\n")
        else:
            min_round = self.initial_round
            print(f"Last payout round is None, searching for transactions from initial operating algo transfer round.({self.initial_round})\n")
        if self.asa_id is not None:
            txn_type = "axfer"
        else:
            txn_type = "pay"
        eligible_tx_list = []
        next_token = str()
        first_loop = True
        while next_token is not None:
            if first_loop is True:
                lotto_address_transaction_search = indexer_client().search_transactions(limit=limit, txn_type=txn_type, min_round=min_round, max_round=None, asset_id=self.asa_id, min_amount=min_amt, max_amount=max_amt, address=self.lotto_address, address_role = "receiver")
            else:
                lotto_address_transaction_search = indexer_client().search_transactions(limit=limit, next_page=next_token, txn_type=txn_type, min_round=min_round, max_round=None, asset_id=self.asa_id, min_amount=min_amt, max_amount=max_amt, address=self.lotto_address, address_role = "receiver")
            eligible_tx_list += lotto_address_transaction_search.get('transactions')
            next_token = lotto_address_transaction_search.get('next_token')
            first_loop = False
        for tx in eligible_tx_list:
            valid_transaction_account_list.append(tx.get("sender"))
        if len(valid_transaction_account_list) > self.max_valid_tx_list_length:
            erroe = "Fishy, too many transactions in the list."
            return erroe
        e_b_count = len(valid_transaction_account_list)
        return e_b_count

    def eligible_bets(self) -> int:
        """
        Returns the number of eligible bets recieved
        """
        lotto_eligible_bets = self.transaction_count()
        return lotto_eligible_bets

    def bets_needed(self) -> int:
        """
        Returns the number of bets needed for the lotto to activate
        """
        lotto_bets_needed = self.amt_bets_required - self.eligible_bets()
        return lotto_bets_needed

    def last_payout_tx_id(self) -> str:
        """
        Returns the last payout transaction id from the lotto account
        """
        print("Checking lotto account for last prize payout tx'id")
        if self.asa_id is None:
            tx_type = "pay"
        else:
            tx_type = "axfer"
        limit = 1
        last_payout = indexer_client().search_transactions(limit=limit, txn_type=tx_type, min_amount=self.min_prize_amount, max_amount=self.max_prize_amount, address=self.lotto_address, address_role = "sender")
        lotto_last_payout_tx_id = last_payout.get("transactions")[0].get("id")
        return lotto_last_payout_tx_id

    def last_winner(self) -> str:
        """
        Returns the last winning address from the lotto account
        """
        print("Checking lotto account for last prize payout address")
        if self.asa_id is None:
            tx_type = "pay"
        else:
            tx_type = "axfer"
        limit = 1
        last_payout = indexer_client().search_transactions(limit=limit, txn_type=tx_type, min_amount=self.min_prize_amount, max_amount=self.max_prize_amount, address=self.lotto_address, address_role = "sender")
        lotto_last_winner = last_payout.get("transactions")[0].get("payment-transaction").get("receiver")
        return lotto_last_winner

    def last_ten(self) -> tuple:
        """
        Returns a tuple containing two lists of the last ten winning addresses and tx id's from the lotto account
        """
        print("Checking lotto account for last ten transactions")
        last_ten_list = []
        address_list = []
        tx_id_list = []
        if self.asa_id is None:
            tx_type = "pay"
        else:
            tx_type = "axfer"
        limit = 10
        next_token = str()
        first_loop = True

        while next_token is not None:
            if first_loop is True:
                payout_check = indexer_client().search_transactions(limit=limit, txn_type=tx_type, min_amount=self.min_prize_amount, max_amount=self.max_prize_amount, address=self.lotto_address, address_role = "sender")
            else:
                payout_check = indexer_client().search_transactions(limit=limit, txn_type=tx_type, min_amount=self.min_prize_amount, max_amount=self.max_prize_amount, address=self.lotto_address, address_role = "sender", next=next_token)
            
            last_ten_list += payout_check.get('transactions')
            next_token = payout_check.get('next_token')
            first_loop = False
        for tx in last_ten_list:
            address_list.append(tx.get('payment-transaction').get('receiver'))
            tx_id_list.append(tx.get("id"))
        last_ten_tuple = (address_list, tx_id_list)
        return last_ten_tuple

    def account(self) -> str:
        """
        Returns the lotto address
        """
        l_a = self.lotto_address
        return l_a
    def asset_id(self) -> int:
        """
        Returns the lotto asset id
        """
        a_id = "0"
        return a_id


class asaLottoInfo:
    """
    This class returns lotto information for an asa lotto
    """
    def __init__(self, lotto_address,reswap_address, initial_round, max_valid_tx, amt_bets_required,bet_amount, prize_amount, asa_id):
        self.lotto_address = lotto_address
        self.reswap_address = reswap_address
        self.initial_round = initial_round
        self.max_valid_tx_list_length = max_valid_tx
        self.amt_bets_required = amt_bets_required
        self.bet_amount = bet_amount
        self.min_bet_amount = self.bet_amount - 1
        self.max_bet_amount = self.bet_amount + 1
        self.prize_amount = prize_amount
        self.min_prize_amount = self.prize_amount - int(self.prize_amount * 0.45)
        self.max_prize_amount = self.prize_amount + 1
        self.asa_id = asa_id

    def balance(self) -> int:
        """
        Returns the account balance for the lotto account in algos
        """
        lotto_account_info = algod_client().account_info(self.lotto_address)
        print(lotto_account_info)
        lotto_balance = int(lotto_account_info.get("amount"))/1000000
        return lotto_balance

    def asa_balance(self) -> int:
        """
        Returns the asa balance for the lotto account in microunits
        """
        lotto_account_info = algod_client().account_asset_info(self.lotto_address, self.asa_id)
        lotto_balance = lotto_account_info.get("asset-holding").get("amount")
        print(f"ASA Balance: {lotto_balance}")
        return lotto_balance

    def check_account_for_prize_payout(self) -> str:
        """
        Check the lotto account for prize payout transactions\n
        """
        print("Checking lotto account for prize payout...")
        payouts = []
        tx_type = "axfer"
        limit = 1
        last_payout_round = None
        payout_check = indexer_client().search_transactions(limit=limit, txn_type=tx_type, min_amount=self.min_prize_amount, max_amount=self.max_prize_amount, address=self.lotto_address, address_role = "sender")
        payouts += payout_check.get('transactions')
        if len(payouts) > 0:
            payout_rounds_list = []
            for tx in payouts:
                payout_rounds_list.append(tx.get("confirmed-round"))
            print(f"This Lotto account has paid out the specified prize amount in these rounds: {payout_rounds_list}")
            last_payout_round = payout_rounds_list[0]
            print(f"End of function returning: {last_payout_round}")
            return last_payout_round
        print("This lotto account has not paid out the specified prize amount, returning: None")
        return last_payout_round

    def transaction_count(self) -> int:
        """
        Count the number of valid tx's into the lotto account after the last payout round\n
        :return: List of eligible accounts
        """
        last_payout_round = self.check_account_for_prize_payout()
        valid_transaction_account_list = []
        min_amt = self.min_bet_amount
        max_amt = self.max_bet_amount
        print("Counting Transactions")
        print(min_amt, max_amt)
        limit = None
        if last_payout_round is not None:
            min_round = str(int(last_payout_round) + 1)
            print(f"Last payout round is not None, searching for transactions from last payout round: {last_payout_round}\n")
        else:
            min_round = self.initial_round
            print(f"Last payout round is None, searching for transactions from initial operating algo transfer round.({self.initial_round})\n")
        txn_type = "axfer"
        eligible_tx_list = []
        next_token = str()
        first_loop = True
        while next_token is not None:
            if first_loop is True:
                lotto_address_transaction_search = indexer_client().search_transactions(limit=limit, txn_type=txn_type, min_round=min_round, max_round=None, asset_id=self.asa_id, min_amount=min_amt, max_amount=max_amt, address=self.lotto_address, address_role = "receiver")
            else:
                lotto_address_transaction_search = indexer_client().search_transactions(limit=limit, next_page=next_token, txn_type=txn_type, min_round=min_round, max_round=None, asset_id=self.asa_id, min_amount=min_amt, max_amount=max_amt, address=self.lotto_address, address_role = "receiver")
            eligible_tx_list += lotto_address_transaction_search.get('transactions')
            next_token = lotto_address_transaction_search.get('next_token')
            first_loop = False
        for tx in eligible_tx_list:
            valid_transaction_account_list.append(tx.get("sender"))
        if len(valid_transaction_account_list) > self.max_valid_tx_list_length:
            erroe = "Fishy, too many transactions in the list."
            return erroe
        e_b_count = len(valid_transaction_account_list)
        return e_b_count

    def eligible_bets(self) -> int:
        """
        Returns the number of eligible bets recieved
        """
        lotto_eligible_bets = self.transaction_count()
        return lotto_eligible_bets

    def bets_needed(self) -> int:
        """
        Returns the number of bets needed for the lotto to activate
        """
        lotto_bets_needed = self.amt_bets_required - self.eligible_bets()
        return lotto_bets_needed

    def last_payout_tx_id(self) -> str:
        """
        Returns the last payout transaction id from the lotto account
        """
        print("Checking lotto account for last prize payout tx'id")
        tx_type = "axfer"
        limit = 1
        last_payout = indexer_client().search_transactions(limit=limit, txn_type=tx_type, min_amount=self.min_prize_amount, max_amount=self.max_prize_amount, address=self.lotto_address, address_role = "sender")
        lotto_last_payout_tx_id = last_payout.get("transactions")[0].get("id")
        return lotto_last_payout_tx_id

    def last_winner(self) -> tuple:
        """
        Returns a tuple containing the last winning address and amount from the lotto account
        """
        print("Checking lotto account for last prize payout address")
        if self.asa_id is None:
            tx_type = "pay"
        else:
            tx_type = "axfer"
        limit = 1
        last_payout = indexer_client().search_transactions(limit=limit, txn_type=tx_type, min_amount=self.min_prize_amount, max_amount=self.max_prize_amount, address=self.lotto_address, address_role = "sender")
        lotto_last_winner = last_payout.get("transactions")[0].get("asset-transfer-transaction").get("receiver")
        lastwinneramt = last_payout.get("transactions")[0].get("asset-transfer-transaction").get("amount")
        winner_tuple = (lotto_last_winner, lastwinneramt)
        return winner_tuple

    def last_ten(self) -> tuple:
        """
        Returns a tuple containing three lists of the last ten winning addresses,tx id's,amounts won from the asa lotto account
        """
        print("Checking lotto account for last ten winning transactions")
        last_ten_list = []
        address_list = []
        tx_id_list = []
        amount_list = []
        tx_type = "axfer"
        limit = 10
        next_token = str()
        first_loop = True

        while next_token is not None:
            if first_loop is True:
                payout_check = indexer_client().search_transactions(limit=limit, txn_type=tx_type, min_amount=self.min_prize_amount, max_amount=self.max_prize_amount, address=self.lotto_address, address_role = "sender")
            else:
                payout_check = indexer_client().search_transactions(limit=limit, txn_type=tx_type, min_amount=self.min_prize_amount, max_amount=self.max_prize_amount, address=self.lotto_address, address_role = "sender", next=next_token)
            
            last_ten_list += payout_check.get('transactions')
            next_token = payout_check.get('next_token')
            first_loop = False
        for tx in last_ten_list:
            if tx.get('asset-transfer-transaction').get('receiver') == self.lotto_address:
                continue
            address_list.append(tx.get('asset-transfer-transaction').get('receiver'))
            tx_id_list.append(tx.get("id"))
            amount_list.append(tx.get('asset-transfer-transaction').get('amount'))
        last_ten_tuple = (address_list, tx_id_list, amount_list)
        return last_ten_tuple

    def account(self) -> str:
        """
        Returns the lotto address
        """
        l_a = self.lotto_address
        return l_a


class reswapInfo:
    """
    Returns information about the reswap account
    """
    def __init__(self):
        self.burn_address = ""
        self.reswap_address = ""
        self.reserve_address =""
        self.tinyman_swap_address = ""
        self.agnr_id = 305992851

    def address(self) -> str:
        """
        Returns the agnr buyback account address
        """
        b_a = self.reswap_address
        return b_a

    def total_buyback(self) -> int:
        """
        Returns the total algo amount exchanged for AGNR
        """
        payouts = []
        address = self.reswap_address
        tx_type = "pay"
        limit = None
        min_amount = 1
        max_amount = None
        next_token = str()
        first_loop = True
        while next_token is not None:
            if first_loop is True:
                payout_check = indexer_client().search_transactions(limit=limit, txn_type=tx_type, min_amount=min_amount, max_amount=max_amount, address=address, address_role = "sender")
            else:
                payout_check = indexer_client().search_transactions(limit=limit, txn_type=tx_type, min_amount=min_amount, max_amount=max_amount, address=address, address_role = "sender", next=next_token)
            payouts += payout_check.get('transactions')
            next_token = payout_check.get('next_token')
            first_loop = False
        if len(payouts) > 0:
            total_buyback_list = []
            for tx in payouts:
                if tx['payment-transaction'].get("receiver") is self.tinyman_swap_address:
                    total_buyback_list.append(tx['payment-transaction'].get("amount"))
            return sum(total_buyback_list)/1000000
        return 0

    def total_burned(self) -> int:
        """
        Returns the total burned amount of AGNR
        """
        agnr_buyback_account_info = indexer_client().lookup_account_assets(self.reswap_address, asset_id=156652797)
        agnr_buyback_total_burned = agnr_buyback_account_info.get("assets")[0].get("amount")
        return agnr_buyback_total_burned
