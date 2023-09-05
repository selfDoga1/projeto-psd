from matrix import Matrix
import Pyro4
import uuid
import os

current_dir = os.path.dirname(os.path.realpath(__file__))
parent_dir = os.path.dirname(current_dir)


def load_matrix(matrix_file_name) -> Matrix:
    matrix_dir = f'{parent_dir}/src/'
    return Matrix(f'{matrix_dir}/{matrix_file_name}')


if __name__ == "__main__":

    print(parent_dir)

    matrix_1 = load_matrix('4_int.txt')
    matrix_2 = load_matrix('4_int.txt')

    ns = Pyro4.locateNS()

    central_server_uri = ns.lookup('central_server')
    central_server = Pyro4.Proxy(central_server_uri)

    worker_uri = ns.lookup('worker')
    central_server.register_worker(worker_uri, uuid.uuid4())
    central_server.register_worker(worker_uri, uuid.uuid4())

    central_server.register_matrices(matrix_1.get_serialized(), matrix_2.get_serialized())
    central_server.prepare()
    central_server.start()

    # result = central_server.divide_and_multiply(matrix_a, matrix_b)

    # for row in result:
    #     print(row)
