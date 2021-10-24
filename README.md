# Algoneer-ASA

Welcome to the Algoneers GitHub Repo!

I created this before I had any clue on how one could actually make an ASA and it turned out to
be much easier coding wise than expected I had assumed it was like an ethereum smart-contract and would require a large amount of code
but Algorand is different the ability to create ASA's is hardcoded into its L1 protocol, which makes it alot easier to create an ASA
with a few commands and a node.

So with that being said I will use this repo to document the creation of Algoneer so it can act as a guide for future devs.

Will update once completed with a step by step detailed guide on how I securely managed this little project.

## Main Points

Token is securely minted with air-gapped, multi-sig accounts, private node, No Ledgers
Token was distributed manually, with goal commands and finally with an automated asset send python script using a private node and the algorand python sdk.

## Setting Up A Node

Algorand dev docs have provided an excellent guide to setting up a local participation node which can be found here [Install a node](https://developer.algorand.org/docs/run-a-node/setup/install/)

## Air Gapped Multi-sig accounts | Secure Minting of Algorand ASA's

I used this guide from Purestake intially to learn the basics of interacting with the Algorand blockchain through a airgapped node.

* [Purestake Blog: How to Set up Multi-sig accounts with offline Keys](https://www.purestake.com/blog/how-to-use-multisig-and-offline-keys-with-algorand/)
* [Purestake Blog: A secure Offline Multi-sig TX](https://www.purestake.com/blog/multisig-transaction-example-5-steps-to-sending-algo-securely/)
* [Purestake Blog: Multi-sig Offline Approach explainer](https://www.purestake.com/blog/multisig-accounts-and-offline-keys-improve-security/)

This provides a nice base for setting up your own offline Multi-sig ASA, depending on your projects requirements. I would suggest getting an actual airgapped dedicated computer as a usb OS will soon become tedious.

## Python SDK | The Sandbox | Autoken.py

Algorand dev docs win again with their quality documentation these two tutorial's will be all you need to get a sandbox up and running.

* [Dev Docs pySDK](https://developer.algorand.org/docs/sdks/python/)
* [Exploring the Sandbox](https://developer.algorand.org/tutorials/exploring-the-algorand-sandbox/)

If your using windows, cause Docker, I recomend installing the windows terminal and the VS code remote wsl extension.

### Autoken.py

Ok so you have Docker installed, windows terminal, wsl2, the pythonsdk installed in wsl, the docker container is running and the remote wsl extension installed in VS code. Also you have minted your asset on the testnet and are ready to distribute.

<samp>Open up your terminal, enter your distro and cd into the sandbox folder</samp>

```bash
cd /mnt/c/Users/$USERNAME/Path_to_sandbox
```
<samp>Enter commands</samp>

```bash
./sandbox up testnet -v
./sandbox status
```
<sub>*turn off your vpn if you run into issues starting the sandbox*</sub>
<samp>Once the sandbox has started, or caught up if its your first time running it, cd into the folder containing the autoken.py script and enter the following command,</samp>

```bash
code .
```
<samp>This should launch a remote instance of VS code connected to WSL:Distro you should see a little green box in the bottom left corner informing you of this status</samp>

<samp>Assuming one is starting from scratch, we can either run the following goal commands in the bash terminal or use the python SDK generate_account.py script to make at least 3 accounts preferably 10 to ~ accounts.</samp>

#### *Python SDK generate_account.py*

```python
from algosdk import account, mnemonic

def generate_algorand_keypair():
    private_key, address = account.generate_account()
    print("My address: {}".format(address))
    print("My private key: {}".format(private_key))
    print("My passphrase: {}".format(mnemonic.from_private_key(private_key)))


generate_algorand_keypair()

# Write down your address, private key, and the passphrase for later usage:
# My address: 
# My private key: 
# My passphrase:
```

<samp>Make note of all account's addresses, private keys, and passphrases. Open add_asset.py in VS code</samp>

<samp>Run</samp>

```bash
./sandbox status
```
<samp>To get the current round, make that the first round and add 1000 for the last round, also the asset ID you will be sending.</samp>

```python
first_valid_round = 17365622
last_valid_round = 17366621
index = 22089866  # identifying index ID of the asset in this case Algoneer!
```
<samp> Input the private key and the address of the account adding the asset</samp>

```python
add_asset('private_key', 'public_key')
```
And run the script! Repeat until all of your test accounts have the asset your sending added.

<samp>Now set aside one account to be your send account load up the send account with enough of the ASA and testnet algo to cover testing of the autoken script and record all of the details in test_Accounts.txt</samp>

```
Create as many test accounts as you like and and save their details here! Make sure you add the asset to each, before running the script!

ACCOUNT 1
My address: 
My private key: 
My passphrase: 
```

<samp>Take your test account address's and cp them into the test_pubK_list.txt, one per line</samp>

```
6FJYFMPVFEKIQTEWYLOSN3QJLIIX74M2LJUX2PPW7V3PK7YZZRXCVTFIZQ
56VH7LJ6WEBFC34CWYP7JQBIHGKWBCJYCULZQPOOHRMZPV5DVCQHJDVHB4
OQIGSARKI5VWGA2SQOWNJMT7S5KEYXPTTPY53BRCLQRSBW2WBIQMTYXRPQ
YSL4FN4N2PP2QZFLSR5ZKOBEJLTK4U5OP76WU3GWY7IVAIEIMHMLHFLTI4
OA23JV5S5CJFNUNMWE3HHTYL3U2GLYIRZWOCZN43PZRB2NW5MQW5XAANBA
```

<samp>Open Autoken.py, modifiy the rounds, the send amount, and the index ID of the asset</samp>

```python
# build transaction
    fee = 1000
    first_valid_round = 17380481
    last_valid_round = 17381479
    gh = "SGO1GKSzyE7IEPItTxCByw9x8FmnrCDexi9/cOUJOiI="
    receiver = key
    amount = 1  # amount of assets to transfer in Microalgos
    index = 22089866  # ID of the asset
```

<samp>Replace private_key and send_address with your private key and send address!</samp>

```python
send_transactions('private_key', 'send_address')
```

_Push Play!_

<samp>The script should run and loop through the account key list, sending one transaction to each until the list is empty.</samp> 


This project was a great introduction into blockchain programming and I have learned alot so much this project has morphed into a DAPP, check back here or the socials for updates.

If this repo has blessed to you to the point you want to give back, buy me a beer,
Algorand address: X4HDO7GP4NCYZZ4OCWDBCKAUXO4XJK3GLTTJGJQ63FNVXSMPL4PBP52RWA