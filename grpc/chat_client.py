import grpc
import chat_pb2_grpc
import chat_pb2

SUCCESS = 0
CONNECTION_ERROR = 1
RETRY_ERROR = 2
MESSAGE = 3

def login(stub):
    u = input("Username? ")
    p = input("Password? ")
    user = chat_pb2.User(username = u, password = p)
    return stub.Login(user)

def register(stub):
    u = input("Username? ")
    p = input("Password? ")
    user = chat_pb2.User(username = u, password = p)
    return stub.Register(user)

def login_or_register(stub):
    resp = input("Welcome! Would you like to (L)ogin to an existing account or (R)egister a new account (Type L or R)?\n").upper()
    while resp not in "LR":
        resp = input("Input not recognized, please type L or R. ").upper()
    return login(stub) if resp == "L" else register(stub)

def run():
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = chat_pb2_grpc.ChatServerStub(channel)

        while True:
            response = login_or_register(stub)
            print(response.responseString)

            if response.retType == SUCCESS:
                break
            elif response.retType == CONNECTION_ERROR:
                exit()

run()
