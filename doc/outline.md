# Outline

## Client

- create message
- send size of message and size of packets in a single fixed-size message.
  need to determine a good size for that message
- await a confirmation from the server
  * *record time*
- transmit message in fixed-size messages
- wait for response once last packet is sent
  * *record time*
- compare received message to sent message. check for bytes which are different



## Server

- listen for initial message
- send confirmation message back and begin listening for payload message
- send back message once it has been received in full
