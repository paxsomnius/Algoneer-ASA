#Atomic AirDrop Goal Commands

#Step 1: Create the Transactions

goal asset send -a 1000000 --assetid 305992851 -f SENDER_PUB_KEY -t RECIEVER_PUB_KEY --firstvalid 16446229 --lastvalid 16447228 -n "Hold And Ye Shall Prosper - AGNR 20:21" -o at0.tx
goal asset send -a 1000000 --assetid 305992851 -f SENDER_PUB_KEY -t RECIEVER_PUB_KEY --firstvalid 16446229 --lastvalid 16447228 -n "Verification in Progress - AGNR 20:21" -o at1.tx
goal asset send -a 1000000 --assetid 305992851 -f SENDER_PUB_KEY -t RECIEVER_PUB_KEY --firstvalid 16446229 --lastvalid 16447228 -n "I like The View From Up Here, The Earth Looks So Pretty - AGNR 20:24" -o at2.tx
goal asset send -a 1000000 --assetid 305992851 -f SENDER_PUB_KEY -t RECIEVER_PUB_KEY --firstvalid 16446229 --lastvalid 16447228 -n "Hold And Ye Shall Prosper - AGNR 20:21" -o at3.tx
goal asset send -a 1000000 --assetid 305992851 -f SENDER_PUB_KEY -t RECIEVER_PUB_KEY --firstvalid 16446229 --lastvalid 16447228 -n "If You Believe in Any Gods, Pray Now! - AGNR 20:22" -o at4.tx
goal asset send -a 1000000 --assetid 305992851 -f SENDER_PUB_KEY -t RECIEVER_PUB_KEY --firstvalid 16446229 --lastvalid 16447228 -n "Get over here! - AGNR 20:22" -o at5.tx
goal asset send -a 1000000 --assetid 305992851 -f SENDER_PUB_KEY -t RECIEVER_PUB_KEY --firstvalid 16446229 --lastvalid 16447228 -n "We all make choices in life, but in the end our choices make us. - AGNR 20:24" -o at6.tx
goal asset send -a 1000000 --assetid 305992851 -f SENDER_PUB_KEY -t RECIEVER_PUB_KEY --firstvalid 16446229 --lastvalid 16447228 -n "When You Judge Others You Judge Yourself - AGNR 20:21" -o at7.tx
goal asset send -a 1000000 --assetid 305992851 -f SENDER_PUB_KEY -t RECIEVER_PUB_KEY --firstvalid 16446229 --lastvalid 16447228 -n "A man chooses; a tool obeys - AGNR 20:23" -o at8.tx
goal asset send -a 1000000 --assetid 305992851 -f SENDER_PUB_KEY -t RECIEVER_PUB_KEY --firstvalid 16446229 --lastvalid 16447228 -n "Only Titans have the courage to walk into the darkness - AGNR 20:22" -o at9.tx
goal asset send -a 1000000 --assetid 305992851 -f SENDER_PUB_KEY -t RECIEVER_PUB_KEY --firstvalid 16446229 --lastvalid 16447228 -n "Hold And Ye Shall Prosper - AGNR 20:21" -o at10.tx
goal asset send -a 1000000 --assetid 305992851 -f SENDER_PUB_KEY -t RECIEVER_PUB_KEY --firstvalid 16446229 --lastvalid 16447228 -n "Hold And Ye Shall Prosper - AGNR 20:21" -o at11.tx
goal asset send -a 1000000 --assetid 305992851 -f SENDER_PUB_KEY -t RECIEVER_PUB_KEY --firstvalid 16446229 --lastvalid 16447228 -n "Hold And Ye Shall Prosper - AGNR 20:21" -o at12.tx
goal asset send -a 1000000 --assetid 305992851 -f SENDER_PUB_KEY -t RECIEVER_PUB_KEY --firstvalid 16446229 --lastvalid 16447228 -n "Hold And Ye Shall Prosper - AGNR 20:21" -o at13.tx
goal asset send -a 1000000 --assetid 305992851 -f SENDER_PUB_KEY -t RECIEVER_PUB_KEY --firstvalid 16446229 --lastvalid 16447228 -n "Hold And Ye Shall Prosper - AGNR 20:21" -o at14.tx
goal asset send -a 1000000 --assetid 305992851 -f SENDER_PUB_KEY -t RECIEVER_PUB_KEY --firstvalid 16446229 --lastvalid 16447228 -n "Hold And Ye Shall Prosper - AGNR 20:21" -o at15.tx

#Step 2: Concatenate outputted single tx's into one max 16
cat at0.tx at1.tx at2.tx at3.tx at4.tx at5.tx at6.tx at7.tx at8.tx at9.tx at10.tx at11.tx at12.tx at13.tx at14.tx at15.tx > combi1.tx

#Step 3: Group concatenated tx's
goal clerk group -i combi1.tx -o g1.tx

#Step 4: Sign Atomic tx seperatly
goal clerk sign -i g1.tx -o sg1.tx
			
			#Optional: Inspect tx file
			goal clerk inspect sg1.tx
	
#Step 5: Send Atomic tx
goal clerk rawsend -f sg1.tx