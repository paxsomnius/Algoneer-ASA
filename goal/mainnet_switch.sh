#!/bin/bash
sudo systemctl stop algorand@$(systemd-escape ${ALGORAND_DATA}) && sleep 3s && sudo systemctl disable algorand@$(systemd-escape ${ALGORAND_DATA}) && sleep 3s && ALGORAND_DATA=/var/lib/algorand && sleep 3s && sudo systemctl start algorand && sleep 3s && ALGORAND_DATA=/var/lib/algorand && goal node status -w 1000





