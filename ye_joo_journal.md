2023.02.08.
Established connection between two computers on same network.
Python's sendall handles encoding & decoding in the process.
Should establish wire protocol for creating account / logging in / sending message / receiving message / deleting account.

https://realpython.com/python-sockets/
https://pythontic.com/modules/socket/send
https://stackoverflow.com/questions/21810776/str-encode-adds-a-b-to-the-front-of-data

2023.02.16.
create_account: supplies username and password (authentication) to ensure only user accesses account
Keeping a list of accounts for now, may start using SQL db at some point. (Same deal for messages)
create_account: currently returning -1 or 0 for failure/success --> should send a message to client rather.
Testing on main() for now, should do unit testing later.
list_accounts: Listing accounts should go through USERS and send them to client --> need protocol for this.
login: should alert client on failure (and type of failure - no id or password not matching)
login: should keep track of who we are logged in as, probably in main (to be implemented)
send_message: should decide between 1) always queueing message and delivering upon request from other user 2) delivering immediately. (2) seems more real world friendly but harder to implement.
receive_messages: should have wire protocol that probably delivers one message at a type. what happens when you fail in the middle?
delete_account & receive_messages: there's a failure case if username is not in USERS or MESSAGES that's not handled at the moment. might be unnecessary (based on how app is designed, we could just take the current user's username) but also makes the functions pretty failure-prone in their absence.
delete_account: returning undelivered messages to sender since that seems the most reasonable (and sender would want to know this!)
side note: make USERS a dict? constant access to username rather than traversing! --> actually gonna do that lol

2023.02.19.
implementing wire protocol on server side. some redundancy in parsing wire protocol arguments (ex: login and register have exact same arguments) --> try to clean up later.
Question for self: should handle_connection have different error codes for different errors that occur? (ex: incorrect password vs. username not found) It doesn't seem that useful at the moment.
for listing accounts & receiving messages, current pack_msg seems failure prone
