from matrix import MatrixSerializer
from dotenv import load_dotenv
from Pyro4.core import Daemon
import Pyro4
import os


DEBUG = True
load_dotenv()


# noinspection DuplicatedCode
class CustomDaemon(Daemon):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @staticmethod
    def serveSimple(objects, host=None, port=0, daemon=None, ns=True, verbose=True, server_uri=None):
        if daemon is None:
            daemon = Daemon(host, port)
        with daemon:
            for obj, name in objects.items():
                localname = name
                uri = daemon.register(obj, localname)
                server = Pyro4.core.Proxy(server_uri)
                print(f'{server.register_remote_worker(uri, server_uri)}')
                print("Worker is running.")
            daemon.requestLoop()


class Worker:
    @staticmethod
    @Pyro4.expose
    def work(matrix_1, matrix_2, chunk):
        matrix_1 = MatrixSerializer().deserialize(matrix_1)
        matrix_2 = MatrixSerializer().deserialize(matrix_2)
        start, end = chunk[0], chunk[1]
        worker_result = []

        for row_index_m1 in range(start, end):
            row = []
            for col_index_m2 in range(matrix_2.col_size):
                product = sum(
                    [
                        matrix_1.rows[row_index_m1][col_index_m1] *
                        matrix_2.get_col(col_index_m2)[row_index_m1]
                        for col_index_m1 in range(matrix_1.col_size)
                    ]
                )
                row.append(product)
            worker_result.append(row)

        return worker_result


if __name__ == "__main__":
    Pyro4.config.SERIALIZER = os.getenv('SERIALIZER')
    server_uri = f'PYRO:{os.getenv("SERVER_NAME")}@{os.getenv("SERVER_HOST")}:{os.getenv("SERVER_PORT")}'

    CustomDaemon().serveSimple(
        {Worker: f'{os.getenv("WORKER_NAME")}'},
        host=os.getenv('WORKER_HOST'),
        port=0,
        server_uri=server_uri
    )
