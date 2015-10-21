import mqttlib
import resource


testAE = resource.AE_create()
testAE.add_api("api1")
testAE.add_apn("apn1")
testAE.add_lbl(["label1"])
# print testAE.show()

Test = resource.req_payload(testAE.show())
Test.add_operation("1")
Test.add_to("mockCSE")
Test.add_rqi("2")
Test.add_fr("AE-ID")
Test.add_ty("2")
Test.add_nm("testAE")
# print Test.show()

Connection = mqttlib.mqttlib()
Connection.connect("127.0.0.1", 1883)
Connection.publish("/oneM2M/req/AE-ID/mockCSE", Test.show())
# mess = Connection.subscribe_and_receive1("/oneM2M/resp/mockCSE/AE-ID", 1, 1)
mess = Connection.subscribe("/oneM2M/resp/mockCSE/AE-ID", 1, 1)
print(mess)
# print(mess['pc'])

Connection = mqttlib.mqttlib()

def connect_to_iotdm(host, port):
    Connection.connect(host, port)
    return Connection


def publish(Connection, topic, message):
    Connection.publish(topic, message)


def subscribe(Connection, topic):
    mess = Connection.subscribe_and_receive1(topic, 1, 1)
    return mess

print(1111)
connection1 = connect_to_iotdm("localhost", 1883)
publish(connection1, "/oneM2M/req/AE-ID/mockCSE", Test.show())
subscribe(connection1, "/oneM2M/resp/mockCSE/AE-ID")