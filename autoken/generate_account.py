from algosdk import account, mnemonic

def generate_algorand_keypair():
    private_key, address = account.generate_account()
    print("My address: {}".format(address))
    print("My private key: {}".format(private_key))
    print("My passphrase: {}".format(mnemonic.from_private_key(private_key)))

# Write down your address, private key, and the passphrase for later usage
# generate_algorand_keypair() # Uncomment this line and run the script to use the keypair generator
# My address: 
# My private key: 
# My passphrase: