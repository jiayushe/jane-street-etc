class Feeder:
    def __init__(self):
        self.bond = []
        self.valbz = []
        self.vale = []
        self.gs = []
        self.ms = []
        self.wfc = []
        self.xlf = []
        self.books = {}

    def get_data(self):
        return self.bond, self.valbz, self.vale, self.gs, self.ms, self.wfc, self.xlf

    def read_market(self):
        return self.books

    def read_in_trade(self, info):
        type1 = info["type"]

        if (type1 == "trade"):
            if (info["symbol"] == "BOND"):
                if (len(self.bond) >= 1000):
                    self.bond.remove(self.bond[0])
                self.bond.append(info["price"])
            if (info["symbol"] == "VALBZ"):
                if (len(self.valbz) >= 1000):
                    self.valbz.remove(self.valbz[0])
                self.valbz.append(info["price"])
            if (info["symbol"] == "VALE"):
                if (len(self.vale) >= 1000):
                    self.vale.remove(self.vale[0])
                self.vale.append(info["price"])
            if (info["symbol"] == "GS"):
                if (len(self.gs) >= 1000):
                    self.gs.remove(self.gs[0])
                self.gs.append(info["price"])
            if (info["symbol"] == "MS"):
                if (len(self.ms) >= 1000):
                    self.ms.remove(self.ms[0])
                self.ms.append(info["price"])
            if (info["symbol"] == "WFC"):
                if (len(self.wfc) >= 1000):
                    self.wfc.remove(self.wfc[0])
                self.wfc.append(info["price"])
            if (info["symbol"] == "XLF"):
                if (len(self.xlf) >= 1000):
                    self.xlf.remove(self.xlf[0])
                self.xlf.append(info["price"])
        elif (type1 == "book"):
            self.books[info["symbol"]] = [info["buy"], info["sell"]]
