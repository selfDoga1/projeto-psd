from dotenv import load_dotenv
from matrix import Matrix
import Pyro4
import uuid
import os

load_dotenv()

current_dir = os.path.dirname(os.path.realpath(__file__))
parent_dir = os.path.dirname(current_dir)


def load_matrix(matrix_file_name) -> Matrix:
    matrix_dir = f'{parent_dir}/src/'
    return Matrix(f'{matrix_dir}/{matrix_file_name}')


if __name__ == "__main__":

    Pyro4.config.HOST = os.getenv('HOST')

    matrix_1 = load_matrix('4_int.txt')
    matrix_2 = load_matrix('4_int.txt')

    ns = Pyro4.locateNS()

    server_uri = ns.lookup('server')
    server = Pyro4.Proxy(server_uri)

    print('server:', server)

    worker_uri = ns.lookup('worker')
    server.register_worker(worker_uri, uuid.uuid4())
    server.register_worker(worker_uri, uuid.uuid4())

    server.register_matrices(matrix_1.get_serialized(), matrix_2.get_serialized())
    server.prepare()
    server.start()

    # result = server.divide_and_multiply(matrix_a, matrix_b)

    # for row in result:
    #     print(row)
