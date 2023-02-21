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

2023.02.20.
OS Error: Bad File Descriptor --> trying to resolve this error. Seems to be triggered by doing conn.close() in handle_connections (getting rid of it makes the error go away). Probably has something to do with trying to receive from an already closed connection.
Cleaned up parsing the request according to wire protocol.
Getting Indexing Error when parsing "list" request because when the user inputs blank but server expects one argument. Fixing on client side.
Adding wildcard matching in list_account functionality. Document for user.
Converted print tests to unit tests. I do wonder if receive_message should work the way it does right now (stacking up strings). An alternative way to do it is to just have a list and then packing arguments, which almost seems more reasonable. (This would require change in server --> client protocol)
Account Deletes --> queueing return message back to MESSAGES to be delievered like any other message, just with the information that the account has been deleted

2023.02.21.
Debugged wildcard matching error (it had to do with wire protocol sending over first char of search term rather than entire string).
Debugged unbound local error for RECEIVED_MESSAGES due to local/global scoping issue.
Changed server side code to the actual delete implementation: once account is deleted, remaining messages get delivered to user before the user leaves.

Generally tested functions in non-grpc chat case. Just one error case.
The initial messaging seems to work but one thing I've tried that doesn't properly work (maybe it's just me):
if yejoo sends evan message, yejoo logs out, evan logs in, evan logs out, then upon log out evan will see message
if yejoo sends evan message, yejoo logs out, evan logs in, evan clicks check message, then there will be no message, when evan tries to log out it will pring PONG?

Started working on grpc server side. Distinction between unary and stream seem useful --> we probably want some of these to be streaming multiple responses rather than strings.
Implemented login and register to be unary.

Thoughts on grpc for tm morning:
1. Create a message-stream listener that will listen to messages from the server --> this could mean not having to deal with getting messages specifically at login?
2. Test making List a unary_stream
3. Maybe Delete/Receive should also get user info and then stream messages
