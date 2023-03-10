# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc

import chat_pb2 as chat__pb2


class ChatServerStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.Ping = channel.unary_unary(
                '/ChatServer/Ping',
                request_serializer=chat__pb2.Empty.SerializeToString,
                response_deserializer=chat__pb2.Response.FromString,
                )
        self.Register = channel.unary_unary(
                '/ChatServer/Register',
                request_serializer=chat__pb2.User.SerializeToString,
                response_deserializer=chat__pb2.Response.FromString,
                )
        self.Login = channel.unary_unary(
                '/ChatServer/Login',
                request_serializer=chat__pb2.User.SerializeToString,
                response_deserializer=chat__pb2.Response.FromString,
                )
        self.Logout = channel.unary_unary(
                '/ChatServer/Logout',
                request_serializer=chat__pb2.Username.SerializeToString,
                response_deserializer=chat__pb2.Response.FromString,
                )
        self.SendMsg = channel.unary_unary(
                '/ChatServer/SendMsg',
                request_serializer=chat__pb2.Message.SerializeToString,
                response_deserializer=chat__pb2.Response.FromString,
                )
        self.List = channel.unary_unary(
                '/ChatServer/List',
                request_serializer=chat__pb2.ListQuery.SerializeToString,
                response_deserializer=chat__pb2.Response.FromString,
                )
        self.Delete = channel.unary_unary(
                '/ChatServer/Delete',
                request_serializer=chat__pb2.Username.SerializeToString,
                response_deserializer=chat__pb2.Response.FromString,
                )
        self.GetMsgs = channel.unary_stream(
                '/ChatServer/GetMsgs',
                request_serializer=chat__pb2.Username.SerializeToString,
                response_deserializer=chat__pb2.Message.FromString,
                )


class ChatServerServicer(object):
    """Missing associated documentation comment in .proto file."""

    def Ping(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def Register(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def Login(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def Logout(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def SendMsg(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def List(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def Delete(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetMsgs(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_ChatServerServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'Ping': grpc.unary_unary_rpc_method_handler(
                    servicer.Ping,
                    request_deserializer=chat__pb2.Empty.FromString,
                    response_serializer=chat__pb2.Response.SerializeToString,
            ),
            'Register': grpc.unary_unary_rpc_method_handler(
                    servicer.Register,
                    request_deserializer=chat__pb2.User.FromString,
                    response_serializer=chat__pb2.Response.SerializeToString,
            ),
            'Login': grpc.unary_unary_rpc_method_handler(
                    servicer.Login,
                    request_deserializer=chat__pb2.User.FromString,
                    response_serializer=chat__pb2.Response.SerializeToString,
            ),
            'Logout': grpc.unary_unary_rpc_method_handler(
                    servicer.Logout,
                    request_deserializer=chat__pb2.Username.FromString,
                    response_serializer=chat__pb2.Response.SerializeToString,
            ),
            'SendMsg': grpc.unary_unary_rpc_method_handler(
                    servicer.SendMsg,
                    request_deserializer=chat__pb2.Message.FromString,
                    response_serializer=chat__pb2.Response.SerializeToString,
            ),
            'List': grpc.unary_unary_rpc_method_handler(
                    servicer.List,
                    request_deserializer=chat__pb2.ListQuery.FromString,
                    response_serializer=chat__pb2.Response.SerializeToString,
            ),
            'Delete': grpc.unary_unary_rpc_method_handler(
                    servicer.Delete,
                    request_deserializer=chat__pb2.Username.FromString,
                    response_serializer=chat__pb2.Response.SerializeToString,
            ),
            'GetMsgs': grpc.unary_stream_rpc_method_handler(
                    servicer.GetMsgs,
                    request_deserializer=chat__pb2.Username.FromString,
                    response_serializer=chat__pb2.Message.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'ChatServer', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class ChatServer(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def Ping(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/ChatServer/Ping',
            chat__pb2.Empty.SerializeToString,
            chat__pb2.Response.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def Register(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/ChatServer/Register',
            chat__pb2.User.SerializeToString,
            chat__pb2.Response.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def Login(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/ChatServer/Login',
            chat__pb2.User.SerializeToString,
            chat__pb2.Response.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def Logout(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/ChatServer/Logout',
            chat__pb2.Username.SerializeToString,
            chat__pb2.Response.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def SendMsg(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/ChatServer/SendMsg',
            chat__pb2.Message.SerializeToString,
            chat__pb2.Response.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def List(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/ChatServer/List',
            chat__pb2.ListQuery.SerializeToString,
            chat__pb2.Response.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def Delete(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/ChatServer/Delete',
            chat__pb2.Username.SerializeToString,
            chat__pb2.Response.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def GetMsgs(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_stream(request, target, '/ChatServer/GetMsgs',
            chat__pb2.Username.SerializeToString,
            chat__pb2.Message.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)
