#!/usr/bin/env python

from misc import *

hddCost = (125.40, 120)
gbCost = (1, 4 )
markup = 33

def space_price(space, addMarkup = True):
	"Calculate the price of space (in Mb)"

	price = (float(hddCost[1]) / hddCost[0]) / 1000.0
	price = price * space
	if addMarkup:
		price = addPercent(price, markup)
	return price

def transfer_price(transfer, addMarkup = True):
	"Calculate the price of transfer (in Mb)"

	price = (float(gbCost[1]) / float(gbCost[0])) / 1000.0
	price = price * transfer
	if addMarkup:
		price = addPercent(price, markup)
	return price

def hosting_price(space, transfer, discount = 0):
	"""Calculate the hosting price

	space    - Mb
	transfer - Mb
	"""

	if discount > 0:
		price = space_price(space) + transfer_price(transfer)
		cost = space_price(space, False) + transfer_price(transfer, False)
		tmp = subPercent(price, discount)
		if (tmp - cost) > 0:
			return tmp
		else:
			return None
	else:
		price = space_price(space) + transfer_price(transfer)
		return price
