import paho.mqtt.client as mqtt

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("$SYS/#")

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))

client = mqtt.Client()
# client.on_connect = on_connect
client.on_message = on_message

client.connect("localhost", 1883, 60)

request_payload = '''
{
    %s
}
'''

class req_payload:
    """
    Create the request payload.
    """

    payload = ""
    def __init__(self, pc):
        self.pc ="\"pc\" : {%s}" % (pc)

    def addOperation(self, op):
        self.op = "\"op\" : \"%s\"," % (op)

    def addTo(self, to):
        self.to = "\"to\" : \"%s\"," % (to)

    def addRqi(self, rqi):
        self.rqi = "\"rqi\" : \"%s\"," % (rqi)

    def addFr(self, fr):
        self.fr = "\"fr\" : \"%s\"," % (fr)

    def addTy(self, ty):
        self.ty = "\"rqi\" : \"%s\"," % (ty)

    def show(self):
        return "{" + self.op + self.to + self.rqi + self.fr + self.ty + self.pc + "}"


class AE_create:
    """
    Create the create_resource_AE "pc".
    """

    def __init__(self):
        self.orr = ""
        self.lbl = ""

    def addApi(self, api):
        self.api = "\"api\" : \"%s\"," % (api)

    def addApn(self, apn):
        self.apn = "\"apn\" : \"%s\"," % (apn)

    def addOr(self, orr):
        self.orr = "\"or\" : \"%s\"," % (orr)

    def addLbl(self, lbl):
        """addLabel, label is a list"""
        assert isinstance(lbl,(list,tuple))
        self.lbl = "\"lbl\" : %s," % (lbl)

    def show(self):
        self.mandatory = self.api + self.apn
        if self.orr != "":
            self.mandatory = self.mandatory + self.orr
        if self.lbl != "":
            self.mandatory = self.mandatory + self.lbl
        return "{" + self.mandatory + "}"


testAE = AE_create()
testAE.addApi("api1")
testAE.addApn("apn1")
testAE.addLbl(["label1"])
print testAE.show()

Test = req_payload(testAE.show())
Test.addOperation("1")
Test.addTo("mockCSE")
Test.addRqi("2")
Test.addFr("AE-ID")
Test.addTy("2")

print Test.show()



def create_resource(client, parent, restype, attribute=None, name=None):
    """Create source in MQTT"""
    restype = int(restype)
    client.publish("/oneM2M/req/AE-ID/mockCSE", "{\"op\" : \"1\",\"to\" : \"mockCSE\",\"rqi\" : \"1\",\"fr\" : \"AE-ID\",\"ty\" : \"2\",\"pc\" :{\"api\":\"mockApplication\",\"apn\":\"mockApp\",\"or\":\"http://ontology_URL\",}}")

def subscirbe_resource(client, topic):
    return client.subscribe(topic, 1)





class connect:
    """
    Create the MQTT connection.
    """

    # def __init__(self, host="localhost", port=1883, time=60):
    #     client.connect(host, port, time)
    #     client.loop_forever()

    def create(self, topic, payload):
        client.publish(topic, payload)

    def subsribe(self, topic):
        client.subscribe(topic, 1)

Connection = connect()
Connection.create("/oneM2M/req/AE-ID/mockCSE", Test.show())



# subcribe will print the on_message
subscirbe_resource(client, "/oneM2M/resp/mockCSE/AE-ID")
#print(client.on_message)

client.loop_forever()