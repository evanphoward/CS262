import grpc
import chat_pb2_grpc
import chat_pb2

HOST = "127.0.0.1"  # Standard loopback interface address (localhost)
PORT = 65432  # Port to listen on (non-privileged ports are > 1023)

USERS = {}
MESSAGES = {}

SUCCESS = 0
CONNECTION_ERROR = 1
RETRY_ERROR = 2
MESSAGE = 3

""" Function to search and list all accounts """
def list_accounts(search):
    accounts = ""
    for username in USERS:
        if fnmatch.fnmatch(username, search):
            accounts += username
            accounts += "\n"

    return accounts

class ChatServerServicer(chat_pb2_grpc.ChatServerServicer):
    def Ping(self, request, context):
        return chat_pb2_grpc.Response(retType=SUCCESS, responseString="PONG!")

    def Login(self, request, context):
        return chat_pb2_grpc.Response(retType=SUCCESS, responseString="Successfully Logged In!")
    
    def Registered(self, request, context):
        return chat_pb2_grpc.Response(retType=SUCCESS, responseString="Successfully Registered!")

    def Logout(self, request, context):
        return chat_pb2_grpc.Response(retType=SUCCESS, responseString="Logout Acknowledged!")

    def SendMsg(self, request, context):
        return chat_pb2_grpc.Response(retType=SUCCESS, responseString="Successfully Sent Message!")

    def List(self, request, context):
        return chat_pb2_grpc.Response(retType=SUCCESS, responseString=list_accounts(request.query))

    def Delete(self, request, context):
        return chat_pb2_grpc.Response(retType=SUCCESS, responseString="Successfully Sent Message!")