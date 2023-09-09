from dotenv import load_dotenv
from matrix import Matrix
import Pyro4
import os

load_dotenv()

current_dir = os.path.dirname(os.path.realpath(__file__))
parent_dir = os.path.dirname(current_dir)


def load_matrix(matrix_file_name) -> Matrix:
    matrix_dir = f'{parent_dir}/src/'
    return Matrix(f'{matrix_dir}/{matrix_file_name}')


if __name__ == "__main__":
    matrix_1 = load_matrix('3_alt.txt')
    matrix_2 = load_matrix('3_alt.txt')

    server_uri = f'PYRO:{os.getenv("SERVER_NAME")}@{os.getenv("SERVER_HOST")}:{os.getenv("SERVER_PORT")}'
    server = Pyro4.core.Proxy(server_uri)

    print(server.register_matrices(matrix_1.get_serialized(), matrix_2.get_serialized()))
    print(server.prepare())
    result, workers_amount, elapsed_time = server.start()

    file_name = (
        f'output/matriz '
        f'{matrix_1.col_size} x {matrix_2.row_size} - '
        f'[{workers_amount} WORKERS] [{elapsed_time}].txt'
    )

    with open(file_name, 'w') as file:
        file.write(f'{matrix_1.col_size} {matrix_2.row_size}\n')
        for row in result:
            line = ' '.join(map(str, row))
            file.write(line + '\n')
