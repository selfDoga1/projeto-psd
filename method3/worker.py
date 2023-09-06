from matrix import MatrixSerializer
from dotenv import load_dotenv
import Pyro4
import os


DEBUG = True
load_dotenv()

ns = Pyro4.locateNS()
server_uri = ns.lookup('server')
server = Pyro4.Proxy(server_uri)


def print_debug(*args):
    if DEBUG:
        print(*args)


class Worker:

    @Pyro4.expose
    def work(self, matrix_1, matrix_2, chunk, worker_id):

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
    Pyro4.config.HOST = os.getenv('HOST')
    Pyro4.config.SERIALIZER = os.getenv('SERIALIZER')
    daemon = Pyro4.Daemon()
    ns = Pyro4.locateNS()

    uri = daemon.register(Worker)
    ns.register('worker', uri)

    print('Worker ready. uri', uri)
    daemon.requestLoop()