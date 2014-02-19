# Outline

All times will be measured in ms. time.time() measures in seconds, so multiply
all times by 1000.

## RTT

### Client

- create message
- send size of message and size of packets in a single fixed-size message.
  need to determine a good size for that message
- await a confirmation from the server
  * *record time*
- transmit message in fixed-size messages
- wait for response once last packet is sent
  * *record time*
- compare received message to sent message. check for bytes which are different



### Server

- listen for initial message
- send confirmation message back and begin listening for payload message
- send back message once it has been received in full


## Throughput

- test upload and download throughput from client's perspective
  - does all of this in a single function call, returning (uptime, downtime)
- begin by testing upload rate
  - transmit a 2B message, as with RTT, so that server knows what's coming
  - once server sends an ACK, begin transmitting message
  - server records the time when first message is received
  - server records the time when the last message is received
  - once client has sent last message, it begins listening for a response
  - server sends the time elapsed in ms back to the client
  - once client has received time elapsed, it stores it and sends an ACK to
    server
- download rate testing
  - once server receives ACK, begins retransmitting received message to client
  - client does exactly as the server did before, recording the time of the
    first and last message
  - client function returns (uptime, downtime) in ms
