

class BidHeuristics:
    total_bids = 0
    total_bids_cleared = 0
    total_delta = 0
    total_charges = 0


    def __init__(self):
        pass


    def _bid_clearance(self, bid_type, bid_price, dam_price):
        if bid_type == "inc" and bid_price <= dam_price:
            return True
        elif bid_type == "dec" and bid_price >= dam_price:
            return True

        return False
    

    def _calculate_delta(self, charge, credit):
        return credit - charge


    def _store_bid(self, delta, charges):
        total_bids_cleared += 1
        total_delta += delta
        total_charges += charges


    def process_bids(self, bid_type: str, rtm_price: float, dam_price: float, bid_price: float, bid_adjustment=0):
        total_bids += 1
        adjusted_bid_price = bid_price + bid_adjustment
        
        if bid_type == "inc" and adjusted_bid_price <= dam_price:
            bid_delta = self._calculate_delta(rtm_price, dam_price)
            charge = rtm_price
            return self._store_bid(bid_delta, charge)
   
        elif bid_type == "dec" and adjusted_bid_price >= dam_price:
            bid_delta =  self._calculate_delta(dam_price, rtm_price)
            charge = dam_price
            return self._store_bid(bid_delta, charge)

        return None
