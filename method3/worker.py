from matrix import MatrixSerializer
import Pyro4
import uuid


DEBUG = True

ns = Pyro4.locateNS()
central_server_uri = ns.lookup('central_server')
central_server = Pyro4.Proxy(central_server_uri)


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
    Pyro4.config.HOST = "localhost"
    Pyro4.config.SERIALIZER = "json"
    daemon = Pyro4.Daemon()
    ns = Pyro4.locateNS()

    uri = daemon.register(Worker)
    ns.register("worker", uri)

    print("Worker ready. uri", uri)
    daemon.requestLoop()