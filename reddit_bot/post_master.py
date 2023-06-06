import json
import os
import configparser
import datetime
import praw
import post_methods as pm

file_path = os.path.abspath(os.path.dirname(__file__))
config = configparser.ConfigParser()
config.read(f'{file_path}/config.ini')
subreddits = ("algoneer")# List of Sub/s to post to
credentials = config['postMaster']['credentials']

with open(credentials, encoding="utf-8") as f:
    creds = json.load(f)
reddit = praw.Reddit(client_id=creds['client_id'],
                     client_secret=creds['client_secret'],
                     user_agent=creds['user_agent'],
                     redirect_uri=creds['redirect_uri'],
                     refresh_token=creds['refresh_token'])
dt = datetime.datetime.now()
timestamp = dt.strftime("%b/%d/%Y %H:%M:%S")
title = f'Algoneer Dotty the DeFi Lotty | {timestamp} --- Mainnet V1'
# Get the lotto data
agnr_1k_100 = pm.asaLottoInfo()
agnr_1m_100 = pm.asaLottoInfo()
algo_1k_1 = pm.AlgoLottoInfo()
algo_10_1 = pm.AlgoLottoInfo()
# Get the buyback data
re = pm.reswapInfo()
# Get the winners

agnr_1k_100_winner_adress = agnr_1k_100.last_ten()[0]
agnr_1k_100_winning_tx_id = agnr_1k_100.last_ten()[1]
agnr_1k_100_winning_amt = agnr_1k_100.last_ten()[2]
agnr_1m_100_winner_adress = agnr_1m_100.last_ten()[0]
agnr_1m_100_winning_tx_id = agnr_1m_100.last_ten()[1]
agnr_1m_100_winning_amt = agnr_1m_100.last_ten()[2]

algo_1k_1_winner_adress = algo_1k_1.last_ten()[0]
algo_1k_1_winning_tx_id = algo_1k_1.last_ten()[1]
algo_10_1_winner_adress = algo_10_1.last_ten()[0]
algo_10_1_winning_tx_id = algo_10_1.last_ten()[1]


selftext = f'''
# Dotty the DeFi Lotty Auto Update

---

The Dotty is an automated lottery game running exclusively on the algorand blockchain!

---
#### How it works:
---
##### The lottery is a simple game, you send the required eligible amount of algo/asa to the respective lotto account, and when the pool reaches the prize amount the lottery is drawn and the winner is chosen at random from the eligible players, the winner is then paid out the prize amount and the pool is reset.
---
#### Jackpots:
##### The large jackpot games have extreme security with multi-sig accounts and keys distributed around the world, held by a third party in high security vaults. The jackpot games will be drawn live on youtube and the winner paid out live on stream.
---
---
##### Security - I and the team have decades of experience with traditional sofware development/secure deployment therefore I am immensely confident when crafting an app that will be used to hold and distribute cryptocurrency. Dotty leans heavily toward security vs usability, and we have taken every precaution to ensure the safety of the users funds.
---
## ReSwap Account Info
#### [View reswap account on AlgoExplorer](https://algoexplorer.io/address/{re.address()})
---
| Account | Total Algo BuyBack |
|:---:|:---:|
|  {re.address()[:15]}...{re.address()[45:]}  |  {re.total_buyback()}   |
---
# Current Live Games
## 1. ***AGNR 1k/100*** | ***1k AGNR*** prize | ***100 AGNR*** entry
#### [View lotto account on AlgoExplorer](https://algoexplorer.io/address/{agnr_1k_100.account()})
---
| Asset ID | Account | 
|:---:|:---:|
|  {agnr_1k_100.asa_id}  |  {agnr_1k_100.lotto_address}  |
| Balance | {agnr_1k_100.balance()} |

---
| Eligible Bets | Bets Needed |
|:---:|:---:|
| {agnr_1k_100.eligible_bets()}  |   {agnr_1k_100.bets_needed()}  |
---
#### Last Winner! 
---

| Winner | Prize | Tx ID |
|:---:|:---:|:---:|
|  1. {agnr_1k_100_winner_adress[0][:10]}...{agnr_1k_100_winner_adress[0][47:]}  |  {agnr_1k_100_winning_amt[0]}  |   [View tx on AlgoExplorer](https://algoexplorer.io/tx/{agnr_1k_100_winning_tx_id[0]})  |

---
# JACKPOT
## 2. ***AGNR 1M/100*** | ***1M AGNR*** prize | ***100 AGNR*** entry
#### [View lotto account on AlgoExplorer](https://algoexplorer.io/address/{agnr_1m_100.account()})
---
| Asset ID | Account |
|:---:|:---:|
|  {agnr_1m_100.asa_id}  |  {agnr_1m_100.lotto_address}  |
| Balance | {agnr_1k_100.balance()} | 
---
| Eligible Bets | Bets Needed |
|:---:|:---:|
| {agnr_1m_100.eligible_bets()}  |   {agnr_1m_100.bets_needed()}  |


---
## 3. ***ALGO 1k/100*** | ***1K ALGO*** prize | ***100 ALGO*** entry
#### [View lotto account on AlgoExplorer](https://algoexplorer.io/address/{algo_1k_1.account()})
---
| Asset ID | Account |
|:---:|:---:|
|  {algo_1k_1.asset_id()}  |  {algo_1k_1.lotto_address}  |
| Balance | {agnr_1k_100.balance()} |  
---
| Eligible Bets | Bets Needed |
|:---:|:---:|
| {algo_1k_1.eligible_bets()}  |   {algo_1k_1.bets_needed()}  |
---
#### Last Winner! 
---

| Winner | Prize | Tx ID |
|:---:|:---:|:---:|
|  1. {algo_1k_1_winner_adress[0][:10]}...{algo_1k_1_winner_adress[0][47:]}  |  {algo_1k_1.prize_amt()}A  |   [View tx on AlgoExplorer](https://algoexplorer.io/tx/{algo_1k_1_winning_tx_id[0]})  |

---
## 4. ***ALGO 10/1*** | ***10 ALGO*** prize | ***1 ALGO*** entry
#### [View lotto account on AlgoExplorer](https://algoexplorer.io/address/{algo_10_1.account()})
---
| Asset ID | Account | Balance | 
|:---:|:---:|:---:|
|  {algo_10_1.asset_id()}  |  {algo_10_1.lotto_address}  |   {algo_10_1.balance()}  |   
---
| Eligible Bets | Bets Needed |
|:---:|:---:|
| {algo_10_1.eligible_bets()}  |   {algo_10_1.bets_needed()}  |
---
#### Last Winner! 
---

| Winner | Prize | Tx ID |
|:---:|:---:|:---:|
|  1. {algo_10_1_winner_adress[0][:10]}...{algo_10_1_winner_adress[0][47:]}  |  {algo_10_1.prize_amt()}A  |   [View tx on AlgoExplorer](https://algoexplorer.io/tx/{algo_10_1_winning_tx_id[0]})  |

---
---
'''
def main():
    """
    Notes: Exchange Moolah for AGNR only
    """
    for rddts in subreddits:
        subreddit = reddit.subreddit(rddts)
        subreddit.submit(title,selftext=selftext)
    print(reddit.user.me())

if __name__ == "__main__":
    main()
