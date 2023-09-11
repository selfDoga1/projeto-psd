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
    matrix_1 = load_matrix('128.txt')
    matrix_2 = load_matrix('128.txt')

    server_uri = f'PYRO:{os.getenv("SERVER_NAME")}@{os.getenv("SERVER_HOST")}:{os.getenv("SERVER_PORT")}'
    server = Pyro4.core.Proxy(server_uri)

    print(server.register_matrices(matrix_1.get_serialized(), matrix_2.get_serialized()))
    print(server.prepare())
    result, workers_amount, elapsed_time, current_time, log = server.start()

    file_name = (
        f'output/[{current_time}] matriz '
        f'{matrix_1.col_size} x {matrix_2.row_size} - '
        f'[{workers_amount} WORKERS] [{elapsed_time}].txt'
    )

    with open(file_name, 'w') as file:
        file.write(f'Variação: P5\n')
        file.write(f'Cores: sem especificação de cores no client\n')
        file.write(f'Computadores Remotos: {workers_amount}\n')
        # for worker_uri in log:
        #     worker = log[worker_uri]
        #     line = f'    {worker_uri}: {worker["threads_amount"]} threads - elapsed time: {worker["elapsed_time"]}'
        #     file.write(line + '\n')

        file.write(f'Número de Linhas: {matrix_2.row_size}\n')
        file.write(f'Número de Colunas: {matrix_1.col_size}\n')
        file.write(f'Tempo de processamento: {elapsed_time}\n\n')

        file.write(f'{matrix_1.col_size} {matrix_2.row_size}\n')
        for row in result:
            line = ' '.join(map(str, row))
            file.write(line + '\n')
