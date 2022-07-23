
class BidHeuristics:

    def __init__(self):
        pass


    def _bid_clearance(self, type, bid, price):
        if type == "inc" and bid <= price:
            return True
        elif type == "dec" and bid >= price:
            return True

        return False
    

    def _calculate_delta(self, charge, credit):
        return credit - charge

    
    def _delta_on_prices(self):
        pass
    
    