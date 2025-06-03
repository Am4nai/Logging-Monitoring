import grpc
import logging_pb2
import logging_pb2_grpc
import time

def send_log(stub):
    logs = [
        logging_pb2.LogEntry(service="web", level="INFO", message="Страница загружена", timestamp=int(time.time())),
        logging_pb2.LogEntry(service="web", level="ERROR", message="Ошибка 500", timestamp=int(time.time())),
        logging_pb2.LogEntry(service="api", level="INFO", message="Запрос обработан", timestamp=int(time.time())),
    ]
    for log in logs:
        stub.SendLog(log)
        print("Лог отправлен")

def query_logs(stub):
    filter = logging_pb2.LogFilter(service="web", level="INFO")
    response = stub.QueryLogs(filter)
    print("Полученные логи:")
    for log in response.logs:
        print(f"{log.service} - {log.level} - {log.message} - {log.timestamp}")

def stream_logs(stub):
    filter = logging_pb2.LogFilter(service="web")
    print("Получение потока логов:")
    for log in stub.StreamLogs(filter):
        print(f"{log.service} - {log.level} - {log.message} - {log.timestamp}")

# Тесты
def run():
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = logging_pb2_grpc.LoggingServiceStub(channel)
        print("Тест SendLog:")
        send_log(stub)
        print("\nТест QueryLogs:")
        query_logs(stub)
        print("\nТест StreamLogs:")
        stream_logs(stub)

if __name__ == '__main__':
    run()