class Strategy():
    # option setting needed
    def __setitem__(self, key, value):
        self.options[key] = value

    # option setting needed
    def __getitem__(self, key):
        return self.options.get(key, '')

    def __init__(self):
        # strategy property
        self.subscribedBooks = {
            'Binance': {
                'pairs': ['ETH-USDT'],
            },
        }

        # self.period =  240 * 60 #1hr
        self.period =  120 * 60 #2hr
        self.options = {}

        # user defined class attribute
        self.arooncount = 0
        self.mficount = 0
        self.down = []
        self.up = []
        self.osc = []
        self.newhighest = 0
        self.newlowest = 0
        self.threenewhigh = 0
        self.threenewlow = 0
        self.aroondown = 0
        self.aroonup = 0
        self.aroonosc = 0

        self.close_price_trace = np.array([1000, 900, 800, 700])
        self.open_price_trace = np.array([1000, 900, 800, 700])
        self.high_price_trace = np.array([1000, 900, 800, 700])
        self.low_price_trace = np.array([1000, 900, 800, 700])
        self.volume_trace = np.array([1000, 900, 800, 700])

    def aroon(self):

        timeperiod = 16

        self.high_price_trace = self.high_price_trace[-17:].astype(np.double)
        self.low_price_trace = self.low_price_trace[-17:].astype(np.double)

        self.down, self.up = talib.AROON(self.high_price_trace, self.low_price_trace, 16)

        self.osc = self.up - self.down

        return self.down[-1:], self.up[-1:], self.osc[-1:]
    
    def threenewhigh(self):

        self.close_price_trace = self.close_price_trace[-4:]


        if self.close_price_trace[3] > self.close_price_trace[2] and self.close_price_trace[3] >self.close_price_trace[1] and self.close_price_trace[3] >self.close_price_trace[0]:
            self.newhighest = 1 #Buy
        else:
            self.newhighest = 2 #Hold

        return int(self.newhighest)

    def threenewlow(self):

        self.close_price_trace = self.close_price_trace[-4:]

        if self.close_price_trace[3] < self.close_price_trace[2] and self.close_price_trace[3] <self.close_price_trace[1] and self.close_price_trace[3] <self.close_price_trace[0]:
            self.newlowest = 1
        else:
            self.newlowest = 2

        return int(self.newlowest)

    # called every self.period
    def trade(self, information):

        exchange = list(information['candles'])[0]
        
        pair = list(information['candles'][exchange])[0]

        self.arooncount += 1
        # self.mficount += 1

        #get_last_order

        closeprice = information['candles'][exchange][pair][0]['close'] #收盤價
        openprice = information['candles'][exchange][pair][0]['open'] #開盤價
        highest = information['candles'][exchange][pair][0]['high'] #最高價
        lowest = information['candles'][exchange][pair][0]['low'] #最低價
        volume = information['candles'][exchange][pair][0]['volume'] #交易量

        self.high_price_trace = np.append(self.high_price_trace, [float(highest)])
        self.low_price_trace = np.append(self.low_price_trace, [float(lowest)])
        self.open_price_trace = np.append(self.open_price_trace, [float(openprice)])
        self.close_price_trace = np.append(self.close_price_trace, [float(closeprice)])
        self.volume_trace = np.append(self.volume_trace, [float(volume)])
        
        self.threenewhigh = self.threenewhigh()
        self.threenewlow = self.threenewlow()
        self.aroondown, self.aroonup, self.aroonosc = self.aroon()

        #BUY
        if self.threenewhigh == 1:
            if self.arooncount > 16 and self.aroondown < 20:
                return [
                    {
                        'exchange': exchange,
                        'amount': 8,
                        'price': -1,
                        'type': 'MARKET',
                        'pair': pair,
                    },
                ]
            else:
                return [
                    {
                        'exchange': exchange,
                        'amount': 5,
                        'price': -1,
                        'type': 'MARKET',
                        'pair': pair,
                    },
                ]
        #SELL
        elif self['assets'][exchange]['ETH'] >0  and self.threenewlow == 1:
            if self.arooncount > 16 and self.aroonup >80:
                return [
                {
                    'exchange': exchange,
                    'amount': -8,
                    'price': -1,
                    'type': 'MARKET',
                    'pair': pair,
                },
            ]
            else:
                return [
                    {
                        'exchange': exchange,
                        'amount': -5,
                        'price': -1,
                        'type': 'MARKET',
                        'pair': pair,
                    },
                ]