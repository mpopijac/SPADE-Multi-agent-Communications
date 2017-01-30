#!/usr/bin/env python
# -*- coding: utf-8 -*-

import spade
import time
import jsonpickle
import sys

from Model.Item import Item

agent_identity = "saleagent@127.0.0.1"
agent_secret = "secret"
agent_repository_identity="repositoryagent@127.0.0.1"
agent_signal = []
available_items = []
order_list=[]
sleeping_time = 0.5

def initial_setup():
    initial_agent = InitialSetup(agent_identity,agent_secret)
    agent_signal.append(1)
    initial_agent.start()
    while True:
        time.sleep(sleeping_time)
        if agent_signal[0] == 0:
            del agent_signal[:]
            break

    initial_agent.stop()
    print "Available items are:"
    for item in available_items:
        item.printItemSale()


def send_message(self, receiver, title, messageBody):
    receiverAgent = spade.AID.aid(name=receiver, addresses=["xmpp://"+receiver])
    self.msg = spade.ACLMessage.ACLMessage()
    self.msg.setOntology(title)
    self.msg.setLanguage("hrvatski")
    self.msg.addReceiver(receiverAgent)
    self.msg.setContent(messageBody)
    self.myAgent.send(self.msg)

def parsing_to_int(value):
    try:
        i = int(value)
        return i
    except ValueError:
        return value

class InitialSetup(spade.Agent.Agent):
    class Inform(spade.Behaviour.OneShotBehaviour):
        def _process(self):
            send_message(self, agent_repository_identity, "informing", "informing")

    class ReceivingItemsOnSale(spade.Behaviour.Behaviour):
        def _process(self):
            self.msg = None
            self.msg = self._receive(True)
            if self.msg:
                del available_items[:]
                received_items=jsonpickle.decode(self.msg.content)
                for item in received_items:
                    available_items.append(Item(item.id, item.name, item.price, item.quantity))
                agent_signal[0]=0

    def _setup(self):
        self.addBehaviour(self.Inform(), None)

        initial_article_template = spade.Behaviour.ACLTemplate()
        initial_article_template.setOntology("on_sale")
        iat = spade.Behaviour.MessageTemplate(initial_article_template)
        self.addBehaviour(self.ReceivingItemsOnSale(), iat)

class Order(spade.Agent.Agent):
    class SendOrder(spade.Behaviour.OneShotBehaviour):
        def _process(self):
            send_message(self, agent_repository_identity, "order", jsonpickle.encode(order_list))

    class ReceivingItemsFromOrder(spade.Behaviour.Behaviour):
        def _process(self):
            self.msg = None
            self.msg = self._receive(True)
            if self.msg:
                message = jsonpickle.decode(self.msg.content)
                print "\n"+message[0]
                for item in message[1]:
                    item.printItem()
                agent_signal[0]=0

    def _setup(self):
        self.addBehaviour(self.SendOrder(), None)

        primanje = spade.Behaviour.ACLTemplate()
        primanje.setOntology("ordered_items")
        ct = spade.Behaviour.MessageTemplate(primanje)
        self.addBehaviour(self.ReceivingItemsFromOrder(), ct)


if __name__ == "__main__":
    initial_setup()
    while True:
        print "Commands:\n P - List of available items \n O - Create order \n X - Exit"
        command = raw_input("Command: ")
        if command == "P" or command == "p":
            initial_setup()
        elif command =="O" or command == "o":
            del order_list[:]
            print "Commands:\n A - Add item to your order \n P - Preview order \n C - Confirm order \n X - Exit from order"
            while True:
                command = raw_input("Command: ")
                if command == "A" or command == "a":
                    ids = raw_input("ID Item: ")
                    id = parsing_to_int(ids)
                    if False == isinstance(id,(int,long)):
                        continue
                    quantitys = raw_input("Quantity: ")
                    quantity = parsing_to_int(quantitys)
                    if False == isinstance(quantity,(int,long)):
                        continue
                    itemOrder=""
                    for item in available_items:
                        if parsing_to_int(item.id) == id:
                            itemOrder = item
                            break
                    if itemOrder!="":
                        added = False
                        for item in order_list:
                            if item.id == ids:
                                item.quantity = str(int(item.quantity)+int(quantitys))
                                added = True
                        if added == False:
                            order_list.append(Item(ids,itemOrder.name,itemOrder.price,quantitys))
                    else:
                        print "The item doesn't exist."
                elif command == "P" or command == "p":
                    print "Order details:"
                    for item in order_list:
                        item.printItem()
                elif command == "C" or command == "c":
                    if order_list:
                        agent_send_order = Order(agent_identity, agent_secret)
                        agent_signal.append(1)
                        agent_send_order.start()
                        while True:
                            time.sleep(sleeping_time)
                            if agent_signal[0] == 0:
                                del agent_signal[:]
                                break
                        agent_send_order.stop()
                    else:
                        print "The order is empty."
                    break
                elif command == "X" or command == "x":
                    break
        elif command =="X" or command == "x":
            sys.exit()
