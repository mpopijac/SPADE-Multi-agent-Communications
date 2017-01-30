#!/usr/bin/env python
# -*- coding: utf-8 -*-
import spade
import jsonpickle

from Model.Item import Item

agent_identity= "supplieragent@127.0.0.1"
agent_secret = "secret"
agent_repository_identity= "repositoryagent@127.0.0.1"


def send_message(self, receiver, title, messageBody):
    receiverAgent = spade.AID.aid(name=receiver, addresses=["xmpp://"+receiver])
    self.msg = spade.ACLMessage.ACLMessage()
    self.msg.setOntology(title)
    self.msg.setLanguage("hrvatski")
    self.msg.addReceiver(receiverAgent)
    self.msg.setContent(messageBody)
    self.myAgent.send(self.msg)


class Supplier(spade.Agent.Agent):
    class Supplying(spade.Behaviour.Behaviour):
        def _process(self):
            self.msg = None
            self.msg = self._receive(True)
            if self.msg:
                items = self.msg.content
                send_message(self,agent_repository_identity,"taking",items)
                items = jsonpickle.decode(items)
                print "Ordered items / Shipped items"
                for item in items:
                    item.printItem()
                print "-----------------------------"

    def _setup(self):
        supplier_template = spade.Behaviour.ACLTemplate()
        supplier_template.setOntology("order")
        it = spade.Behaviour.MessageTemplate(supplier_template)
        self.addBehaviour(self.Supplying(), it)

if __name__ == "__main__":
    agent = Supplier(agent_identity, agent_secret)
    agent.start()