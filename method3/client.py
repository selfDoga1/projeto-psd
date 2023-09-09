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

    matrix_1 = load_matrix('128.txt')
    matrix_2 = load_matrix('128.txt')

    server_uri = f'PYRO:{os.getenv("SERVER_NAME")}@{os.getenv("SERVER_HOST")}:{os.getenv("SERVER_PORT")}'
    server = Pyro4.core.Proxy(server_uri)

    print(server.register_matrices(matrix_1.get_serialized(), matrix_2.get_serialized()))
    print(server.prepare())
    server.start()

