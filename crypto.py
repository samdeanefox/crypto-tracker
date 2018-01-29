import requests
import json
from pprint import pprint

POSITION_FILEPATH = 'position.json'

def ceiling_div(top, bottom):
	return ((top - 1) // bottom) + 1

def repeat_to_length(string_to_expand, length):
   return (string_to_expand * ((length/len(string_to_expand))+1))[:length]

def format_to_cell(value, cell_length):
	value = str(value)
	return_str = ''
	l = len(value)
	if l > cell_length-2:
		value = value[:cell_length-2]
	pre_space = (cell_length-l) // 2
	post_space = ceiling_div(cell_length-l, 2)
	return_str += repeat_to_length(' ', pre_space)
	return_str += value
	return_str += repeat_to_length(' ', post_space)
	return return_str + '|'

def format_dollar(value):
	val = '$' + str(round(float(value), 2))
	pieces = val.split('.')
	if len(pieces) < 2:
		val += '.00'
	elif len(pieces[1]) == 1:
		val += '0'
	return val

def format_percent(value):
	return str(round(float(value), 3)) + '%'


# Fetch data from CoinMarketCap
try:
	response = requests.get("https://api.coinmarketcap.com/v1/ticker/")
	response.raise_for_status()
	all_currencies = response.json()

# deal with exceptions by accessing the returned json and printing out why
except requests.exceptions.HTTPError as e:
	print "%s: %s (%s)" % (
		e.response.status_code,
		e.response.json['code'],
		e.response.json['message']
	)
	exit()

# Read my position from json file
with open(POSITION_FILEPATH) as data_file:
        my_position = json.load(data_file)

bars = '----------------------------------------------------------------------------------------------------'
table = '\n\n\n' + bars + '\n'
table += '|   COIN   |    PRICE    |  BUY PRICE  |     AMOUNT     |    POSITION    |   % GAIN   |   $ GAIN   |\n'
table += bars + '\n'

watchlist_bars = '--------------------------'
watchlist_table =  watchlist_bars + '\n'
watchlist_table += '|   COIN   |    PRICE    |\n'
watchlist_table += watchlist_bars + '\n'

total_data = []
# Iterate through currencies and produce table
for currency in all_currencies:
	symbol = currency['symbol']
	# Append to table
	if symbol in my_position['my_currencies']:
		# Amount
		amount = str(my_position['my_currencies'][symbol]['amount'])
		# Price
		price = round(float(currency['price_usd']), 4)
		if price < 10.0:
			price = '$' + str(price)
		else:
			price = format_dollar(price)
		# Position
		position = format_dollar(float(amount) * float(price[1:]))
		# Buy Price
		buy_price = float(my_position['my_currencies'][symbol]['buy_price'])
		# Current Price
		current_price = float(price[1:])
		# Percent Gain
		if buy_price == current_price:
			p_gain = '0%'
		else:
			p_gain = format_percent(100*(current_price-buy_price) / buy_price)
		# Dollar gain
		d_gain = format_dollar((current_price*float(amount))-(buy_price*float(amount)))
		# Format buy price
		buy_price = format_dollar(buy_price)

		# Append ticker
		table += '|   ' + symbol
		ind = 7 - len(symbol)
		for i in range(0, ind):
			table += ' '
		table += '|'

		# Append price
		table += format_to_cell(price, 13)

		# Append buy price
		table += format_to_cell(buy_price, 13)

		# Append amount
		table += format_to_cell(amount, 16)

		# Append position
		table += format_to_cell(position, 16)

		# Append percent gain
		table += format_to_cell(p_gain, 12)

		# Append dollar gain
		table += format_to_cell(d_gain, 12) + '\n'

		total_cost = float(my_position['my_currencies'][symbol]['buy_price']) * float(my_position['my_currencies'][symbol]['amount'])
		total_pos = float(position[1:])
		total_p_gain = float(p_gain[:-1])
		total_d_gain = float(d_gain[1:])
		total_data.append((total_cost, total_pos, total_p_gain, total_d_gain))

	# Append to watchlist table
	elif symbol in my_position['watchlist']:
		price = round(float(currency['price_usd']), 4)
		# Append ticker
		watchlist_table += '|   ' + symbol
		ind = 7 - len(symbol)
		for i in range(0, ind):
			watchlist_table += ' '
		watchlist_table += '|'
		watchlist_table += format_to_cell(price, 13) + '\n'

# Tally totals		
total = [0, 0, 0, 0]
for data in total_data:
	total[0] += data[0]
	total[1] += data[1]
	total[2] += data[2]
	total[3] += data[3]
total[2] = total[2] / len(total_data)
table += bars + '\n'
table += '|   TOTAL  | ----------- |' + format_to_cell(format_dollar(total[0]), 13)
table += ' -------------- |' + format_to_cell(format_dollar(total[1]), 16)
table += format_to_cell(format_percent(total[2]), 12)
table += format_to_cell(format_dollar(total[3]), 12)
table += '\n' + bars + '\n'
print table

# Print watchlist is applicable
if len(my_position['watchlist']) > 0:
	watchlist_table += watchlist_bars + '\n'
	print '        WATCHLIST\n' + watchlist_table

# Print total investment info
investment = my_position['total_investment']
if investment > 0:
	print 'TOTAL INVESTMENT: ' + format_dollar(investment)
	print 'TOTAL NOW:        ' + format_dollar(total[1])
	print 'TOTAL GAIN:       ' + format_dollar(total[1] - investment)
	print 'PERCENT GAIN:     ' + format_percent(100*(total[1]-investment) / investment)
	print '\n\n\n'