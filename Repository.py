#!/usr/bin/env python
# -*- coding: utf-8 -*-
import spade
import jsonpickle

from Model.Item import Item

config_file = "config-repository.txt"
agent_identity= "repositoryagent@127.0.0.1"
agent_secret = "secret"

agent_supplier_identity= "supplieragent@127.0.0.1"

minimum_order_quantity = []
minimum_quantity_on_stock = []
items_on_stock =[]


def _loading_configuration():
    with open(config_file, "r") as f:
        for line in f:
            if line.__contains__("minimum_order_quantiti"):
                minimum_order_quantity_line = line.replace("minimum_order_quantiti=", "")
                minimum_order_quantity.append(minimum_order_quantity_line.replace("\n", ""))
                continue
            if line.__contains__("minimum_quantity_on_stock"):
                minimum_quantity_on_stock_line = line.replace("minimum_quantity_on_stock=","")
                minimum_quantity_on_stock.append(minimum_quantity_on_stock_line.replace("\n", ""))
                continue
            if line.__contains__("items_in_stock_on_start"):
                line = line.replace("items_in_stock_on_start=", "")
                line = line.split(";")
                for s in line:
                    item = s.split(",")
                    if item.__len__() == 4:
                        item_obj = Item(item[0], item[1], item[2], item[3])
                        items_on_stock.append(item_obj)
    print "The initial state is loaded:"
    for item in items_on_stock:
        item.printItem()
    print "Minimum order quantity is " + minimum_order_quantity[0] + " pieces."
    print "Minimum quantity on stock per item is "+minimum_quantity_on_stock[0]+"."

def send_message(self, receiver, title, messageBody):
    receiverAgent = spade.AID.aid(name=receiver, addresses=["xmpp://"+receiver])
    self.msg = spade.ACLMessage.ACLMessage()
    self.msg.setOntology(title)
    self.msg.setLanguage("hrvatski")
    self.msg.addReceiver(receiverAgent)
    self.msg.setContent(messageBody)
    self.myAgent.send(self.msg)

def processing_order(order_list):
    order_message =[]
    order = []
    additional_message = ""
    for order_item in order_list:
        for available_item in items_on_stock:
            if order_item.id == available_item.id:
                if int(order_item.quantity) <= int(available_item.quantity):
                    item= Item(order_item.id,order_item.name,order_item.price,order_item.quantity)
                    order.append(item)
                    available_item.quantity = str(int(available_item.quantity)-int(order_item.quantity))
                elif int(order_item.quantity) > int(available_item.quantity):
                    item = Item(order_item.id, order_item.name, order_item.price, available_item.quantity)
                    order.append(item)
                    available_item.quantity = "0"
                    if additional_message =="":
                        additional_message = "Unsupplied items will be available in a future order: \n"
                    if additional_message != "":
                        additional_message += " It is not delivered all the quantity of items "+order_item.name+".\n"

    if additional_message == "":
        additional_message = "All items from order are delivered."

    order_message.append(additional_message)
    order_message.append(order)
    return order_message

def check_stock(self):
    items_need_to_be_ordered=[]
    for item in items_on_stock:
        if int(item.quantity) < int(minimum_quantity_on_stock[0]):
            quantity = int(minimum_order_quantity[0])
            while (quantity+int(item.quantity))<int(minimum_quantity_on_stock[0]):
                quantity += 1

            item_ = Item(item.id, item.name, item.price, str(quantity))
            items_need_to_be_ordered.append(item_)

    if items_need_to_be_ordered:
        print "Print orders for suppliers:"
        for item in items_need_to_be_ordered:
            item.printItem()
        send_message(self,agent_supplier_identity,"order",jsonpickle.encode(items_need_to_be_ordered))


class Repository(spade.Agent.Agent):
    class InformingSale(spade.Behaviour.Behaviour):
        def _process(self):
            self.msg = None
            self.msg = self._receive(True)
            if self.msg:
                agent_sale_identity = self.msg.sender.getName()
                print "Sending a message with a list of items."
                send_message(self, agent_sale_identity, "on_sale", jsonpickle.encode(items_on_stock))

    class ReceivingOrder(spade.Behaviour.Behaviour):
        def _process(self):
            self.msg = None
            self.msg = self._receive(True)
            if self.msg:
                order_list = jsonpickle.decode(self.msg.content)
                message = processing_order(order_list)
                agent_sale_identity = self.msg.sender.getName()
                print "Sending a message with list of ordered items."
                send_message(self, agent_sale_identity, "ordered_items", jsonpickle.encode(message))
                check_stock(self)

    class TakingItems(spade.Behaviour.Behaviour):
        def _process(self):
            self.msg = None
            self.msg = self._receive(True)
            if self.msg:
                items = jsonpickle.decode(self.msg.content)
                print "Old state of stock:"
                for item in items_on_stock:
                    item.printItem()
                print "Received items:"
                for item in items:
                    item.printItem()
                print "New state of stock:"
                for item in items_on_stock:
                    for new_item in items:
                        if new_item.id == item.id:
                            item.quantity=str(int(item.quantity)+int(new_item.quantity))
                            break
                    item.printItem()

    def _setup(self):
        informing_template = spade.Behaviour.ACLTemplate()
        informing_template.setOntology("informing")
        it = spade.Behaviour.MessageTemplate(informing_template)
        self.addBehaviour(self.InformingSale(), it)

        order_template = spade.Behaviour.ACLTemplate()
        order_template.setOntology("order")
        ot = spade.Behaviour.MessageTemplate(order_template)
        self.addBehaviour(self.ReceivingOrder(), ot)

        taking_template = spade.Behaviour.ACLTemplate()
        taking_template.setOntology("taking")
        ct = spade.Behaviour.MessageTemplate(taking_template)
        self.addBehaviour(self.TakingItems(), ct)


if __name__ == "__main__":
    _loading_configuration()
    agent = Repository(agent_identity, agent_secret)
    agent.start()


