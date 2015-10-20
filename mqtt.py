import paho.mqtt.client as mqtt
import time
from robot.libraries.DateTime import convert_time
import re
import paho.mqtt.publish as publish
from robot.api import logger

# # The callback for when the client receives a CONNACK response from the server.
# def on_connect(client, userdata, flags, rc):
#     print("Connected with result code "+str(rc))
#
#     # Subscribing in on_connect() means that if we lose the connection and
#     # reconnect then subscriptions will be renewed.
#     client.subscribe("$SYS/#")
#
# # The callback for when a PUBLISH message is received from the server.
# def on_message(client, userdata, msg):
#     print(msg.topic+" "+str(msg.payload))
#
# client = mqtt.Client()
# # client.on_connect = on_connect
# client.on_message = on_message
#
# client.connect("localhost", 1883, 60)

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
        self._orr = ""
        self._lbl = ""

    def add_api(self, api):
        self.api = "\"api\" : \"%s\"," % (api)

    def add_apn(self, apn):
        self.apn = "\"apn\" : \"%s\"," % (apn)

    def add_or(self, orr):
        self._orr = "\"or\" : \"%s\"," % (orr)

    def add_lbl(self, lbl):
        """addLabel, label is a list"""
        assert isinstance(lbl,(list,tuple))
        self._lbl = "\"lbl\" : %s," % (lbl)

    def show(self):
        self.mandatory = self.api + self.apn
        if self._orr != "":
            self.mandatory += self._orr
        if self._lbl != "":
            self.mandatory += self._lbl
        return "{" + self.mandatory + "}"


testAE = AE_create()
testAE.add_api("api1")
testAE.add_apn("apn1")
testAE.add_lbl(["label1"])
print testAE.show()

Test = req_payload(testAE.show())
Test.addOperation("1")
Test.addTo("mockCSE")
Test.addRqi("2")
Test.addFr("AE-ID")
Test.addTy("2")

print Test.show()



# def create_resource(client, parent, restype, attribute=None, name=None):
#     """Create source in MQTT"""
#     restype = int(restype)
#     client.publish("/oneM2M/req/AE-ID/mockCSE", "{\"op\" : \"1\",\"to\" : \"mockCSE\",\"rqi\" : \"1\",\"fr\" : \"AE-ID\",\"ty\" : \"2\",\"pc\" :{\"api\":\"mockApplication\",\"apn\":\"mockApp\",\"or\":\"http://ontology_URL\",}}")
#
# def subscirbe_resource(client, topic):
#     return client.subscribe(topic, 1)
#
#
#


class MQTT(object):

    # Timeout used for all blocking loop* functions. This serves as a
    # safeguard to not block forever, in case of unexpected/unhandled errors
    LOOP_TIMEOUT = '5 seconds'

    def __init__(self, loop_timeout=LOOP_TIMEOUT):
        self._loop_timeout = convert_time(loop_timeout)
        #self._mqttc = mqtt.Client()

    def connect(self, broker, port=1883, client_id="", clean_session=True):

        """ Connect to an MQTT broker. This is a pre-requisite step for publish
        and subscribe keywords.
        `broker` MQTT broker host
        `port` broker port (default 1883)
        `client_id` if not specified, a random id is generated
        `clean_session` specifies the clean session flag for the connection
        Examples:
        Connect to a broker with default port and client id
        | Connect | 127.0.0.1 |
        Connect to a broker by specifying the port and client id explicitly
        | Connect | 127.0.0.1 | 1883 | test.client |
        Connect to a broker with clean session flag set to false
        | Connect | 127.0.0.1 | clean_session=${false} |
        """
        logger.info('Connecting to %s at port %s' % (broker, port))
        self._connected = False
        self._unexpected_disconnect = False
        self._mqttc = mqtt.Client(client_id, clean_session)

        # set callbacks
        self._mqttc.on_connect = self._on_connect
        self._mqttc.on_disconnect = self._on_disconnect

        self._mqttc.connect(broker, int(port))

        timer_start = time.time()
        while time.time() < timer_start + self._loop_timeout:
            if self._connected or self._unexpected_disconnect:
                break;
            self._mqttc.loop()

        if self._unexpected_disconnect:
            raise RuntimeError("The client disconnected unexpectedly")
        logger.debug('client_id: %s' % self._mqttc._client_id)
        return self._mqttc

    def publish(self, topic, message=None, qos=0, retain=False):

        """ Publish a message to a topic with specified qos and retained flag.
        It is required that a connection has been established using `Connect`
        keyword before using this keyword.
        `topic` topic to which the message will be published
        `message` message payload to publish
        `qos` qos of the message
        `retain` retained flag
        Examples:
        | Publish | test/test | test message | 1 | ${false} |
        """
        logger.info('Publish topic: %s, message: %s, qos: %s, retain: %s'
            % (topic, message, qos, retain))
        self._mid = -1
        self._mqttc.on_publish = self._on_publish
        result, mid = self._mqttc.publish(topic, message, int(qos), retain)
        if result != 0:
            raise RuntimeError('Error publishing: %s' % result)

        timer_start = time.time()
        while time.time() < timer_start + self._loop_timeout:
            if mid == self._mid:
                break;
            self._mqttc.loop()

        if mid != self._mid:
            logger.warn('mid wasn\'t matched: %s' % mid)
        # client.publish(topic, message)


    def subscribe(self, topic, qos, timeout=1, limit=1):
        """ Subscribe to a topic and return a list of message payloads received
            within the specified time.
        `topic` topic to subscribe to
        `qos` quality of service for the subscription
        `timeout` duration of subscription
        `limit` the max number of payloads that will be returned. Specify 0
            for no limit
        Examples:
        Subscribe and get a list of all messages received within 5 seconds
        | ${messages}= | Subscribe | test/test | qos=1 | timeout=5 | limit=0 |
        Subscribe and get 1st message received within 60 seconds
        | @{messages}= | Subscribe | test/test | qos=1 | timeout=60 | limit=1 |
        | Length should be | ${messages} | 1 |
        """
        seconds = convert_time(timeout)
        self._messages = []
        limit = int(limit)

        logger.info('Subscribing to topic: %s' % topic)
        self._mqttc.subscribe(str(topic), int(qos))
        self._mqttc.on_message = self._on_message_list

        timer_start = time.time()
        while time.time() < timer_start + seconds:
            if limit == 0 or len(self._messages) < limit:
                self._mqttc.loop()
            else:
                # workaround for client to ack the publish. Otherwise,
                # it seems that if client disconnects quickly, broker
                # will not get the ack and publish the message again on
                # next connect.
                time.sleep(1)
                break
        return self._messages

    def subscribe_and_receive1(self, topic, qos, timeout=1):
            """ Subscribe to a topic and return one message payloads received
                within the specified time.
            `topic` topic to subscribe to
            `qos` quality of service for the subscription
            `timeout` duration of subscription
            Examples:
            Subscribe and get one message received within 5 seconds
            | ${messages}= | Subscribe | test/test | qos=1 | timeout=5
            """
            seconds = convert_time(timeout)
            self._message = ""

            logger.info('Subscribing to topic: %s' % topic)
            self._mqttc.subscribe(str(topic), int(qos))
            self._mqttc.on_message = self._on_message_one

            timer_start = time.time()
            while time.time() < timer_start + seconds:
                self._mqttc.loop()
            return str(self._message)

    def subscribe_and_validate(self, topic, qos, payload, timeout=1):

        """ Subscribe to a topic and validate that the specified payload is
        received within timeout. It is required that a connection has been
        established using `Connect` keyword. The payload can be specified as
        a python regular expression. If the specified payload is not received
        within timeout, an AssertionError is thrown.
        `topic` topic to subscribe to
        `qos` quality of service for the subscription
        `payload` payload (message) that is expected to arrive
        `timeout` time to wait for the payload to arrive
        Examples:
        | Subscribe And Validate | test/test | 1 | test message |
        """
        seconds = convert_time(timeout)
        self._verified = False

        logger.info('Subscribing to topic: %s' % topic)
        self._mqttc.subscribe(str(topic), int(qos))
        self._payload = str(payload)
        self._mqttc.on_message = self._on_message

        timer_start = time.time()
        while time.time() < timer_start + seconds:
            if self._verified:
                break
            self._mqttc.loop()

        if not self._verified:
            raise AssertionError("The expected payload didn't arrive in the topic")

    def unsubscribe(self, topic):

        """ Unsubscribe the client from the specified topic.
        `topic` topic to unsubscribe from
        Example:
        | Unsubscribe | test/mqtt_test |
        """
        self._unsubscribed = False
        self._mqttc.on_unsubscribe = self._on_unsubscribe
        self._mqttc.unsubscribe(str(topic))

        timer_start = time.time()
        while (not self._unsubscribed and
                time.time() < timer_start + self._loop_timeout):
            self._mqttc.loop()

        if not self._unsubscribed:
            logger.warn('Client didn\'t receive an unsubscribe callback')

    def disconnect(self):

        """ Disconnect from MQTT Broker.
        Example:
        | Disconnect |
        """
        self._disconnected = False
        self._unexpected_disconnect = False
        self._mqttc.on_disconnect = self._on_disconnect

        self._mqttc.disconnect()

        timer_start = time.time()
        while time.time() < timer_start + self._loop_timeout:
            if self._disconnected or self._unexpected_disconnect:
                break;
            self._mqttc.loop()
        if self._unexpected_disconnect:
            raise RuntimeError("The client disconnected unexpectedly")

    def publish_single(self, topic, payload=None, qos=0, retain=False,
            hostname="localhost", port=1883, client_id="", keepalive=60,
            will=None, auth=None, tls=None, protocol=mqtt.MQTTv31):

        """ Publish a single message and disconnect. This keyword uses the
        [http://eclipse.org/paho/clients/python/docs/#single|single]
        function of publish module.
        `topic` topic to which the message will be published
        `payload` message payload to publish (default None)
        `qos` qos of the message (default 0)
        `retain` retain flag (True or False, default False)
        `hostname` MQTT broker host (default localhost)
        `port` broker port (default 1883)
        `client_id` if not specified, a random id is generated
        `keepalive` keepalive timeout value for client
        `will` a dict containing will parameters for client:
            will = {'topic': "<topic>", 'payload':"<payload">, 'qos':<qos>,
                'retain':<retain>}
        `auth` a dict containing authentication parameters for the client:
            auth = {'username':"<username>", 'password':"<password>"}
        `tls` a dict containing TLS configuration parameters for the client:
            dict = {'ca_certs':"<ca_certs>", 'certfile':"<certfile>",
                'keyfile':"<keyfile>", 'tls_version':"<tls_version>",
                'ciphers':"<ciphers">}
        `protocol` MQTT protocol version (MQTTv31 or MQTTv311)
        Example:
        Publish a message on specified topic and disconnect:
        | Publish Single | topic=t/mqtt | payload=test | hostname=127.0.0.1 |
        """
        logger.info('Publishing to: %s:%s, topic: %s, payload: %s, qos: %s' %
                    (hostname, port, topic, payload, qos))
        publish.single(topic, payload, qos, retain, hostname, port,
                        client_id, keepalive, will, auth, tls, protocol)

    def publish_multiple(self, msgs, hostname="localhost", port=1883,
            client_id="", keepalive=60, will=None, auth=None,
            tls=None, protocol=mqtt.MQTTv31):

        """ Publish multiple messages and disconnect. This keyword uses the
        [http://eclipse.org/paho/clients/python/docs/#multiple|multiple]
        function of publish module.
        `msgs` a list of messages to publish. Each message is either a dict
                or a tuple. If a dict, it must be of the form:
                msg = {'topic':"<topic>", 'payload':"<payload>", 'qos':<qos>,
                        'retain':<retain>}
                Only the topic must be present. Default values will be used
                for any missing arguments. If a tuple, then it must be of the
                form:
                ("<topic>", "<payload>", qos, retain)
                See `publish single` for the description of hostname, port,
                client_id, keepalive, will, auth, tls, protocol.
        Example:
        | ${msg1} | Create Dictionary | topic=${topic} | payload=message 1 |
        | ${msg2} | Create Dictionary | topic=${topic} | payload=message 2 |
        | ${msg3} | Create Dictionary | topic=${topic} | payload=message 3 |
        | @{msgs} | Create List | ${msg1} | ${msg2} | ${msg3} |
        | Publish Multiple | msgs=${msgs} | hostname=127.0.0.1 |
        """
        logger.info('Publishing to: %s:%s, msgs: %s' %
                    (hostname, port, msgs))
        publish.multiple(msgs, hostname, port, client_id, keepalive,
                        will, auth, tls, protocol)

    def _on_message(self, client, userdata, message):
        logger.debug('Received message: %s on topic: %s with QoS: %s'
            % (str(message.payload), message.topic, str(message.qos)))
        self._verified = re.match(self._payload, str(message.payload))

    def _on_message_list(self, client, userdata, message):
        logger.debug('Received message: %s on topic: %s with QoS: %s'
            % (str(message.payload), message.topic, str(message.qos)))
        self._messages.append(str(message.payload))

    def _on_message_one(self, client, userdata, message):
        """Return only on message."""
        logger.debug('Received message: %s on topic: %s with QoS: %s'
            % (str(message.payload), message.topic, str(message.qos)))
        self._message = (str(message.payload))

    def _on_connect(self, client, userdata, flags, rc):
        self._connected = True if rc == 0 else False

    def _on_disconnect(self, client, userdata, rc):
        if rc == 0:
            self._disconnected = True
            self._unexpected_disconnect = False
        else:
            self._unexpected_disconnect = True

    def _on_unsubscribe(self, client, userdata, mid):
        self._unsubscribed = True

    def _on_publish(self, client, userdata, mid):
        self._mid = mid


Connection = MQTT()
Connection.connect("127.0.0.1", 1883)
Connection.publish("/oneM2M/req/AE-ID/mockCSE", Test.show())
mess = Connection.subscribe_and_receive1("/oneM2M/resp/mockCSE/AE-ID", 1, 1)
print(mess)


# Test1 = MQTTKeywords.MQTTKeywords()
# Test1.connect("127.0.0.1", 1883)
# Test1.publish("/oneM2M/req/AE-ID/mockCSE", Test.show())
# mess = Test1.subscribe("/oneM2M/resp/mockCSE/AE-ID", 1, 1, 0)
# print(mess)

# subcribe will print the on_message
# subscirbe_resource(client, "/oneM2M/resp/mockCSE/AE-ID")
#print(client.on_message)

#client.loop_forever()