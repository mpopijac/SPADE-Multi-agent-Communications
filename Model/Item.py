#!/usr/bin/env python
# -*- coding: utf-8 -*-

class Item:
    def __init__(self, id, name, price, quantity):
        self.id = id
        self.name = name
        self.price = price
        self.quantity = quantity

    def printItem(self):
        print "ID:" + self.id + ", name: " + self.name + ", price: " + self.price + ", quantity:" + self.quantity

    def printItemSale(self):
        print "ID: " + self.id + ", name: " + self.name + ", price: " + self.price
