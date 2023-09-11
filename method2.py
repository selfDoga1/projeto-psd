from matrix import Matrix
from threading import Thread
import os
import time
import numpy as np

current_dir = os.path.dirname(os.path.realpath(__file__))

# noinspection PyUnresolvedReferences
class CustomThread(Thread):
    def __init__(self, target, args=()):
        super().__init__(target=target, args=args)
        self._return = None

    def run(self):
        if self._target is not None:
            self._return = self._target(*self._args)
    def join(self, timeout=None):
        super().join(timeout)
        return self._return


# noinspection DuplicatedCode,PyShadowingNames
class MethodTwo:
    def __init__(self, variation, cores_amount, matrix_1_file, matrix_2_file) -> None:
        self.matrix_1 = Matrix(f'{current_dir}/src/{matrix_1_file}')
        self.matrix_2 = Matrix(f'{current_dir}/src/{matrix_2_file}')
        self.threads_amount = self.get_threads_amount(variation, cores_amount)
        self.variation = variation
        self.cores_amount = cores_amount
        self.result, self.start_time, self.end_time = self.get_multi_matrix()

        self.elapsed_time = self.end_time - self.start_time
        # self.elapsed_time = '{:.10f}'.format(self.elapsed_time)

        print('elapsed time: ', self.elapsed_time)

        self.make_output_file()

    def get_threads_amount(self, variation, cores_amount):
        if variation == 'P2':
            return cores_amount
        elif variation == 'P3':
            return cores_amount * 2
        elif variation == 'P4':
            return cores_amount // 2

    def _get_chunks(self, rows, threads_amount) -> list:
        result = []
        chunk_per_thread = rows // threads_amount
        rest_division = rows % threads_amount
        start = 0

        for i in range(threads_amount):
            end = start + chunk_per_thread
            if i < rest_division:
                end += 1
            result.append([start, end])
            start = end

        return result

    def _process(self, start, end) -> list:
        thread_result = []

        # for row_index_m1 in range(start, end):
        #     row = []
        #     for col_index_m2 in range(self.matrix_2.col_size):
        #         product = sum(
        #             [
        #                 self.matrix_1.rows[row_index_m1][col_index_m1] *
        #                 self.matrix_2.get_col(col_index_m2)[row_index_m1]
        #                 for col_index_m1 in range(self.matrix_1.col_size)
        #             ]
        #         )
        #         row.append(product)
        #     thread_result.append(row)

        array_matrix_1 = np.array(self.matrix_1.rows)
        array_matrix_2 = np.array(self.matrix_2.rows)

        sub_matrix_1 = array_matrix_1[start:end]
        sub_matrix_2 = array_matrix_2

        sub_result = np.dot(sub_matrix_1, sub_matrix_2.T)

        for row in sub_result:
            thread_result.append(row.tolist())

        return thread_result

    def get_multi_matrix(self):
        if self.matrix_1.col_size != self.matrix_2.row_size:
            raise ValueError("O número de colunas da matriz 1 deve ser igual ao número de linhas da matriz 2!")

        global_result = []
        threads_list = []
        chunks = self._get_chunks(self.matrix_1.row_size, self.threads_amount)

        for chunk in chunks:
            thread = CustomThread(target=self._process, args=[chunk[0], chunk[1]])
            threads_list.append(thread)

        start_time = time.time()

        for thread in threads_list:
            thread.start()

        for thread in threads_list:
            global_result.extend(thread.join())

        end_time = time.time()

        return global_result, start_time, end_time

    def make_output_file(self) -> None:
        file_name = (f'output/matriz '
                     f'{self.matrix_1.col_size} x {self.matrix_2.row_size} - '
                     f'[{self.threads_amount} THR] [{self.elapsed_time}].txt')

        with open(file_name, 'w') as file:
            file.write(f'Variação: {self.variation}\n')
            file.write(f'Cores: {self.cores_amount}\n')
            file.write('Computadores Remotos: Sem computadores remotos\n')
            file.write(f'Número de Linhas: {self.matrix_2.row_size}\n')
            file.write(f'Número de Colunas: {self.matrix_1.col_size}\n')
            file.write(f'Tempo de processamento: {self.elapsed_time}\n\n')

            file.write(f'{self.matrix_1.col_size} {self.matrix_2.row_size}\n')
            for row in self.result:
                line = ' '.join(map(str, row))
                file.write(line + '\n')


if __name__ == '__main__':
    variation = 'P4'
    cores_amount = 4
    matrix_1_file = '128.txt'
    matrix_2_file = '128.txt'
    MethodTwo(variation, cores_amount, matrix_1_file, matrix_2_file)
