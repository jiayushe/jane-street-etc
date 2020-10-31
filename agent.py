import bot
import feeder

INFPOS = 100000000
INFNEG = -100000000

def mean(l):
    if len(l) == 0:
        return 0
    return sum(l) / len(l)

def init_bond(exchange):
    bot.buy_symbol(exchange, 'BOND', 999, 50)
    bot.sell_symbol(exchange, 'BOND', 1001, 50)

def operate_bond(exchange, message, data: feeder.Feeder):
    if message['type'] == 'fill' and message['symbol'] == 'BOND':
        if message['dir'] == 'BUY':
            bot.buy_symbol(exchange, 'BOND', 999, message['size'])
        else:
            bot.sell_symbol(exchange, 'BOND', 1001, message['size'])

def _decide_val(valbz_price, vale_price):
    num = 0
    flag = 'NO_OP'
    if (vale_price > valbz_price):
        num = 10 / (vale_price - valbz_price)
        num = int(num + 1)
        flag = 'VALBZ'
    elif (vale_price < valbz_price):
        num = 10 / (valbz_price - vale_price)
        num = int(num + 1)
        flag = 'VALE'
    return flag, num

def operate_val(exchange, message, data: feeder.Feeder):
    if (message['type'] == 'trade') and ((message['symbol'] == 'VALBZ') or (message['symbol'] == 'VALE')):
        bond, valbz, vale, gs, ms, wfc, xlf = data.get_data()
        valbz_price = mean(valbz[-30:])
        vale_price = mean(vale[-30:])
        book = data.read_market()
        if (len(valbz) > 0 and len(vale) > 0 and ('VALBZ' in book) and ('VALE' in book)):
            flag, num = _decide_val(valbz_price, vale_price)
            buy_valbz, sell_valbz = book['VALBZ']
            buy_vale, sell_vale = book['VALE']
            if (flag == 'VALBZ') and (num < 5) and len(buy_valbz) and len(sell_vale):
                bot.buy_symbol(exchange, 'VALBZ', buy_valbz[0][0] + 1, 7)
                bot.buy_convert(exchange, 'VALBZ', 10)
                bot.sell_symbol(exchange, 'VALE', sell_vale[0][0] - 1, 7)
            if (flag == 'VALE') and (num < 5) and len(buy_vale) and len(sell_valbz):
                bot.buy_symbol(exchange, 'VALE', buy_vale[0][0] + 1, 7)
                bot.buy_convert(exchange, 'VALE', 10)
                bot.sell_symbol(exchange, 'VALBZ', sell_valbz[0][0] - 1, 7)

def operate_xlf(exchange, message, data: feeder.Feeder):
    if (message['type'] == 'trade') and (message['symbol'] == 'XLF'):
        bond, valbz, vale, gs, ms, wfc, xlf = data.get_data()
        if len(bond) == 0 or len(gs) == 0 or len(ms) == 0 or len(wfc) == 0 or len(xlf) == 0:
            return

        partition = 5
        bond_price = mean(bond[-partition:])
        gs_price = mean(gs[-partition:])
        ms_price = mean(ms[-partition:])
        wfc_price = mean(wfc[-partition:])
        xlf_price = mean(xlf[-partition:])

        book = data.read_market()
        if 'BOND' in book:
            buy_bond, sell_bond = book['BOND']
        if 'GS' in book:
            buy_gs, sell_gs = book['GS']
        if 'MS' in book:
            buy_ms, sell_ms = book['MS']
        if 'WFC' in book:
            buy_wfc, sell_wfc = book['WFC']
        if 'XLF' in book:
            buy_xlf, sell_xlf = book['XLF']

        size = 2

        if (10 * xlf_price + 100 < (3 * bond_price + 2 * gs_price + 3 * ms_price + 2 * wfc_price)) \
            and len(buy_xlf) and len(sell_bond) and len(sell_gs) and len(sell_ms) and len(sell_wfc):
            bot.buy_symbol(exchange, "XLF", buy_xlf[0][0] + 1, 10 * size)
            bot.sell_convert(exchange, "XLF", 10 * size)
            bot.sell_symbol(exchange, "BOND", sell_bond[0][0] - 1, 3 * size)
            bot.sell_symbol(exchange, "GS", sell_gs[0][0] - 1, 2 * size)
            bot.sell_symbol(exchange, "MS", sell_ms[0][0] - 1, 3 * size)
            bot.sell_symbol(exchange, "WFC", sell_wfc[0][0] - 1, 2 * size)
        elif (10 * xlf_price - 100 > (3 * bond_price + 2 * gs_price + 3 * ms_price + 2 * wfc_price)) \
            and len(sell_xlf) and len(buy_bond) and len(buy_gs) and len(buy_ms) and len(buy_wfc):
            bot.buy_symbol(exchange, "BOND", buy_bond[0][0] + 1, 3 * size)
            bot.buy_symbol(exchange, "GS", buy_gs[0][0] + 1, 2 * size)
            bot.buy_symbol(exchange, "MS", buy_ms[0][0] + 1, 3 * size)
            bot.buy_symbol(exchange, "WFC", buy_wfc[0][0] + 1, 2 * size)
            bot.buy_convert(exchange, "XLF", 10 * size)
            bot.sell_symbol(exchange, "XLF", sell_xlf[0][0] - 1, 10 * size)

def _is_buy(price_list):
    if len(price_list) < 9:
        return INFPOS
    else:
        ratel = []
        for item in range(len(price_list[-7:-1])):
            ratel.append(
                (price_list[item + 1] - price_list[item]) / (price_list[item] + 1e-10))
        if (ratel[-1] < 0 and ratel[-2] < 0 and ratel[-3] < 0 and ratel[-4] < 0 and ratel[-5] < 0 and ratel[-6] < 0):
            return sum(ratel) - 0.1
        else:
            return INFPOS

def _is_sell(price_list):
    if len(price_list) < 9:
        return INFNEG
    else:
        ratel = []
        for item in range(len(price_list[-7:-1])):
            ratel.append(
                (price_list[item + 1] - price_list[item]) / (price_list[item] + 1e-10))
        if (ratel[-1] > 0 and ratel[-2] > 0 and ratel[-3] > 0):
            return sum(ratel) + 0.1
        else:
            return INFNEG

def operate_buy(exchange, message, data: feeder.Feeder):
    if (message['type'] == 'trade'):
        bond, valbz, vale, gs, ms, wfc, xlf = data.get_data()

        book = data.read_market()
        if 'VALBZ' in book:
            buy_valbz, sell_valbz = book['VALBZ']
        if 'VALE' in book:
            buy_vale, sell_vale = book['VALE']
        if 'GS' in book:
            buy_gs, sell_gs = book['GS']
        if 'MS' in book:
            buy_ms, sell_ms = book['MS']
        if 'WFC' in book:
            buy_wfc, sell_wfc = book['WFC']
        if 'XLF' in book:
            buy_xlf, sell_xlf = book['XLF']

        list1 = [_is_buy(valbz), _is_buy(vale), _is_buy(gs), _is_buy(ms), _is_buy(wfc), _is_buy(xlf)]
        list2 = [_is_sell(valbz), _is_sell(vale), _is_sell(gs), _is_sell(ms), _is_sell(wfc), _is_sell(xlf)]

        if min(list1) != INFPOS:
            pos = list1.index(min(list1))
            if pos == 0 and len(buy_valbz):
                bot.buy_symbol(exchange, 'VALBZ', buy_valbz[0][0] + 2, 10)
            if pos == 1 and len(buy_vale):
                bot.buy_symbol(exchange, 'VALE', buy_vale[0][0] + 2, 10)
            if pos == 2 and len(buy_gs):
                bot.buy_symbol(exchange, 'GS', buy_gs[0][0] + 2, 10)
            if pos == 3 and len(buy_ms):
                bot.buy_symbol(exchange, 'MS', buy_ms[0][0] + 2, 10)
            if pos == 4 and len(buy_wfc):
                bot.buy_symbol(exchange, 'WFC', buy_wfc[0][0] + 2, 10)
            if pos == 5 and len(buy_xlf):
                bot.buy_symbol(exchange, 'XLF', buy_xlf[0][0] + 2, 10)

        if max(list2) != INFNEG:
            pos = list2.index(max(list2))
            if pos == 0 and len(sell_valbz):
                bot.buy_symbol(exchange, 'VALBZ', sell_valbz[0][0] - 2, 10)
            if pos == 1 and len(sell_vale):
                bot.buy_symbol(exchange, 'VALE', sell_vale[0][0] - 2, 10)
            if pos == 2 and len(sell_gs):
                bot.buy_symbol(exchange, 'GS', sell_gs[0][0] - 2, 10)
            if pos == 3 and len(sell_ms):
                bot.buy_symbol(exchange, 'MS', sell_ms[0][0] - 2, 10)
            if pos == 4 and len(sell_wfc):
                bot.buy_symbol(exchange, 'WFC', sell_wfc[0][0] - 2, 10)
            if pos == 5 and len(sell_xlf):
                bot.buy_symbol(exchange, 'XLF', sell_xlf[0][0] - 2, 10)
