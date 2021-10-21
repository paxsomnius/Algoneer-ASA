#!/bin/bash
sudo systemctl stop algorand && sleep 3 && ALGORAND_DATA=/var/lib/algorand_testnet && sleep 3 && sudo systemctl enable algorand@$(systemd-escape ${ALGORAND_DATA}) && sleep 3 && sudo systemctl start algorand@$(systemd-escape ${ALGORAND_DATA}) && sleep 3 && goal node status -w 1000


