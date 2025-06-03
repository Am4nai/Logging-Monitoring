import grpc
from concurrent import futures
import logging_pb2
import logging_pb2_grpc

logs = []

class LoggingService(logging_pb2_grpc.LoggingServiceServicer):
    def SendLog(self, request, context):
        logs.append(request)
        print(f"Получен лог: {request.service} - {request.level} - {request.message}")
        return logging_pb2.Empty()

    def QueryLogs(self, request, context):
        filtered_logs = logs
        if request.service:
            filtered_logs = [log for log in filtered_logs if log.service == request.service]
        if request.level:
            filtered_logs = [log for log in filtered_logs if log.level == request.level]
        return logging_pb2.LogResponse(logs=filtered_logs)

    def StreamLogs(self, request, context):
        filtered_logs = logs
        if request.service:
            filtered_logs = [log for log in filtered_logs if log.service == request.service]
        if request.level:
            filtered_logs = [log for log in filtered_logs if log.level == request.level]
        for log in filtered_logs:
            yield log

# Создаём сервер gRPC
def serverRun():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    logging_pb2_grpc.add_LoggingServiceServicer_to_server(LoggingService(), server)
    server.add_insecure_port('[::]:50051')
    print("Сервер запущен на порту 50051")
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    serverRun()