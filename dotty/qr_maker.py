import qrcode
import lotteries as lot

def algo_qr_coder(p_k,lotto_name,amt=1000):
    """
    This function Creates QR codes for the Lotto accounts, outputs qr into /qrcodes.
    Example URI scheme for Algorand QR codes: "algorand://KXZ4CX3PDXWTKXJ3JHCCRYVZZBPQBWJWXQPTVZQ46X6EPUDLUFGVJHJZ7I?amount=10000000&note=HelloWorldimPAX"
    """
    dff=f"/home/pax/Desktop/AGNR/Dapp/DAPP_AGNR_LOTTO/qrcodes/{lotto_name}.png"
    uri=f"algorand://{p_k}?amount={amt}&note=Game: {lotto_name}, Bet Amount: {amt}"
    img = qrcode.make(uri)
    type(img)
    img.save(dff)

def asa_qr_coder(p_k,lotto_name,a_id,amt):
    """
    This function Creates QR codes for the Lotto accounts, outputs qr into /qrcodes.
    Example URI scheme for Algorand QR codes: "algorand://KXZ4CX3PDXWTKXJ3JHCCRYVZZBPQBWJWXQPTVZQ46X6EPUDLUFGVJHJZ7I?amount=10000000&note=HelloWorldimPAX"
    """
    dff=f"/home/pax/Desktop/AGNR/Dapp/DAPP_AGNR_LOTTO/qrcodes/{lotto_name}.png"
    uri=f"algorand://{p_k}?amount={amt}&asset={a_id}&note=Game: {lotto_name}, Bet Amount: {amt}"
    img = qrcode.make(uri)
    type(img)
    img.save(dff)

if __name__ == "__main__":
    asa_qr_coder() # Public Key, Lotto Name, ASA ID, Bet Amount for single QR Processing
    algo_lotto = [] # List Of algo lottery objects for batch QR Processing
    asa_lotto = [] # List Of asa lottery objects for batch QR Processing
    for lotto in algo_lotto:
        algo_qr_coder(lotto.lotto_address,lotto.game_id,lotto.bet_amount)
    for lotto in asa_lotto:
        asa_qr_coder(lotto.lotto_address,lotto.game_id,lotto.asa_id,lotto.bet_amount)
