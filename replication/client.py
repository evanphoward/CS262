import socket
import time

HOSTS = ["127.0.0.1", "127.0.0.1", "127.0.0.1"]  # The three server's hostname or IP address
PORT = 65432  # The port used by the server

# Connection Codes
SERVER = 0
CLIENT = 1

# Operation Codes
PING = 0
REGISTER = 1
LOGIN = 2
SEND_MSG = 3
LOGOUT = 4
LIST = 5
DELETE = 6

# Response Codes
CONNECTION_ERROR = 1
RETRY_ERROR = 2
MESSAGE = 3

""" Class that represents a Client """
class Client():
    """ Initialize Client Object """
    def __init__(self):
        self.primary_server_id = 0
        self.logged_in_user = ()
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.received_messages = []

    """ Makes a request to the socket. req_type is the type of request and args are the arguments needed for that request """
    def make_request(self, req_type, args):
        """ Gets a response from server and parses it according to wire protocol """
        def parse_response(resp):
            if not resp:
                return [CONNECTION_ERROR, "Error: Lost connection to server"]
            i = 0
            responses = []
            while i < len(resp):
                ret_type = resp[i]
                msg_length = int(resp[i + 1])
                responses.append((ret_type, resp[i + 2 : i + 2 + msg_length].decode()))
                i += 2 + msg_length
            return responses

        """ Packs a string argument into a bytes object (appends the length of the string to the front and turns everything into bytes) """
        def pack_arg(arg):
            byte_arg = arg.encode()
            if len(arg) >= 256:
                return 2, "Argument too long"
            return 0, (len(byte_arg)).to_bytes(1, byteorder='big') + byte_arg

        """ If connection to server fails, move over to another server """
        def failover():
            time.sleep(0.1)
            self.primary_server_id = (self.primary_server_id + 1) % 3
            self.initialize_socket()
            self.login()
            self.socket.sendall(packed_req)

        packed_req = (req_type).to_bytes(1, byteorder='big') + (len(args)).to_bytes(1, byteorder='big')

        # Pack each argument into a bytes array and append them together to send to the server
        for i, arg in enumerate(args):
            err, packed_arg = pack_arg(arg)
            if err != 0:
                return RETRY_ERROR, REQUEST_ERRS[req_type][i]
            packed_req += packed_arg
        try:
            self.socket.sendall(packed_req)
        except:
            # Switch to a backup server if socket can't send data to server
            failover()

        # Get parsed responses from the server
        responses = parse_response(self.socket.recv(1024))
        if responses[0] == CONNECTION_ERROR:
            # Switch to backup server if socket can't receive data from server
            failover()
            responses = parse_response(self.socket.recv(1024))
        # If all of the responses are messages for the user, keep waiting until we get the response to this request
        while all(resp[0] == MESSAGE for resp in responses):
            responses.extend(parse_response(self.socket.recv(1024)))

        # Print all the messages to the user, and return the response to this request
        ret = responses[0]
        if len(responses) > 1:
            for resp in responses:
                if resp[0] == MESSAGE:
                    self.received_messages.append(resp[1])
                else:
                    ret = resp
        return ret

    """ Function for client login request """
    def login(self):
        # Use logged in user if it exists, enables logging back in on failover
        if not self.logged_in_user:
            u = input("Username? ")
            p = input("Password? ")
            self.logged_in_user = (u, p)
        err, msg = self.make_request(LOGIN, self.logged_in_user)
        if err != 0:
            self.logged_in_user = None
        return err, msg

    """ Function for client register request """
    def register(self):
        u = input("Username? ")
        p = input("Password? ")
        err, msg = self.make_request(REGISTER, (u, p))
        if err == 0:
            self.logged_in_user = (u, p)
        return err, msg

    """ Function for login/register branch """
    def login_or_register(self):
        resp = input("Welcome! Would you like to (L)ogin to an existing account or (R)egister a new account (Type L or R)?\n").upper()
        while resp not in "LR":
            resp = input("Input not recognized, please type L or R. ").upper()
        return self.login() if resp == "L" else self.register()

    """ Function for client logout request """
    def logout(self):
        ret = self.make_request(LOGOUT, ())
        self.socket.close()
        return ret

    """ Function for client ping request """
    def ping(self):
        return self.make_request(PING, ())

    """ Function for client list requst """
    def list_users(self):
        search = input("Please supply a search term (Leave blank to see all users, use * as a wildcard)\n")
        # Blank Input by User
        if not search:
            return self.make_request(LIST, ())
        # User Input
        return self.make_request(LIST, (search,))

    """ Function for client send rquest """
    def send_msg(self, user):
        receiver = input("Who would you like to send a message to? ")
        msg = input("Please type your message (Max 256 characters)\n")
        return self.make_request(SEND_MSG, (user, receiver, msg))

    """ Function for client delete request """
    def delete_account(self, user):
        ret = self.make_request(DELETE, (user,))
        self.socket.close()
        return ret

    """ Create socket for connection and send connection message to server """
    def initialize_socket(self, tries=3):
        # If we've tried all three servers, return an error
        if tries == 0:
            return -1
        self.socket.close()
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # If the current primary server doesn't work, try the next server (wrapping back around)
        try:
            self.socket.connect((HOSTS[self.primary_server_id], PORT + self.primary_server_id))
        except:
            self.primary_server_id = (self.primary_server_id + 1) % 3
            return self.initialize_socket(tries - 1)
        connection_message = (CLIENT).to_bytes(1, byteorder = 'big')
        self.socket.sendall(connection_message)
        time.sleep(0.05)
        return 0

    """ Function that runs the client """
    def run(self):
        err = self.initialize_socket()
        if err == -1:
            print("No working server found, exiting")
            return

        # on connection, user must login or register
        err, msg = self.login_or_register()
        print(msg)
        if err == CONNECTION_ERROR:
            return
        while err == RETRY_ERROR:
            err, msg = self.login_or_register()
            print(msg)
            if err == CONNECTION_ERROR:
                return

        # once logged in, user can use full functionality of the app
        while True:
            opt = print("Welcome " + self.logged_in_user[0] + "! Would you like to (C)heck messages, (L)ist users, (S)end a message, (D)elete your account, or L(o)gout?")
            opt = input("").upper()

            while opt not in "CLSDO":
                opt = input("Input not recognized, please type C, L, S, D, or O. ").upper()

            # Check messages
            if opt == "C":
                self.ping()
                if self.received_messages:
                    print("New Messages:")
                    print(''.join(self.received_messages))
                else:
                    print("No New Messages!")
                self.received_messages = []

            # List users on the app
            elif opt == "L":
                err, msg = self.list_users()
                print(msg)
                if err == CONNECTION_ERROR:
                    self.socket.close()
                    break

            # Send message to another user
            elif opt == "S":
                err, msg = self.send_msg(self.logged_in_user[0])
                print(msg)
                if err == CONNECTION_ERROR:
                    self.socket.close()
                    break

            # Delete user's own account
            elif opt == "D":
                _, msg = self.delete_account(self.logged_in_user[0])
                if self.received_messages:
                    print("Before you go, here are your new messages:")
                    print(''.join(self.received_messages))
                print(msg)
                break

            # Log out
            elif opt == "O":
                _, msg = self.logout()
                if self.received_messages:
                    print("Before you go, here are your new messages:")
                    print(''.join(self.received_messages))
                print(msg)
                break
def main():
    client = Client()
    client.run()

main()
