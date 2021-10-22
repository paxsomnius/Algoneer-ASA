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

### Autoken.py

This project was a great introduction into blockchain programming and I have learned alot so much this project has morphed into a DAPP, check back here or the socials for updates.
