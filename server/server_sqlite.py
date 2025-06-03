import grpc
from concurrent import futures
import sqlite3
import threading
import logging_pb2
import logging_pb2_grpc

local = threading.local()

def get_db_connection():
    if not hasattr(local, 'conn'):
        local.conn = sqlite3.connect('../data/database.sqlite')
        local.cursor = local.conn.cursor()
        with open('../data/schema.sql', 'r') as f:
            local.cursor.executescript(f.read())
        local.conn.commit()
    return local.conn, local.cursor

class LoggingService(logging_pb2_grpc.LoggingServiceServicer):
    def SendLog(self, request, context):
        conn, cursor = get_db_connection()
        query = "INSERT INTO logs (service, level, message, timestamp) VALUES (?, ?, ?, ?)"
        cursor.execute(query, (request.service, request.level, request.message, request.timestamp))
        conn.commit()
        print(f"Получен лог: {request.service} - {request.level} - {request.message}")
        return logging_pb2.Empty()

    def QueryLogs(self, request, context):
        conn, cursor = get_db_connection()
        query = "SELECT service, level, message, timestamp FROM logs"
        conditions = []
        params = []
        if request.service:
            conditions.append("service = ?")
            params.append(request.service)
        if request.level:
            conditions.append("level = ?")
            params.append(request.level)
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        cursor.execute(query, params)
        logs = []
        for row in cursor.fetchall():
            log = logging_pb2.LogEntry(
                service=row[0], level=row[1], message=row[2], timestamp=row[3]
            )
            logs.append(log)
        return logging_pb2.LogResponse(logs=logs)

    def StreamLogs(self, request, context):
        conn, cursor = get_db_connection()
        query = "SELECT service, level, message, timestamp FROM logs"
        conditions = []
        params = []
        if request.service:
            conditions.append("service = ?")
            params.append(request.service)
        if request.level:
            conditions.append("level = ?")
            params.append(request.level)
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        cursor.execute(query, params)
        for row in cursor.fetchall():
            log = logging_pb2.LogEntry(
                service=row[0], level=row[1], message=row[2], timestamp=row[3]
            )
            yield log

def serverRun():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    logging_pb2_grpc.add_LoggingServiceServicer_to_server(LoggingService(), server)
    server.add_insecure_port('[::]:50051')
    print("Сервер запущен на порту 50051")
    server.start()
    try:
        server.wait_for_termination()
    except KeyboardInterrupt:
        if hasattr(local, 'conn'):
            local.conn.close()
        print("Сервер остановлен")

if __name__ == '__main__':
    serverRun()