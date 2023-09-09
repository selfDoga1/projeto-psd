from matrix import Matrix
from threading import Thread
import os
import time


current_dir = os.path.dirname(os.path.realpath(__file__))
THREADS_AMOUNT = 5


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
    def __init__(self) -> None:
        self.matrix_1 = Matrix(f'{current_dir}/src/128.txt')
        self.matrix_2 = Matrix(f'{current_dir}/src/128.txt')
        self.result, self.start_time, self.end_time = self.get_multi_matrix()

        self.elapsed_time = self.end_time - self.start_time
        self.elapsed_time = '{:.10f}'.format(self.elapsed_time)

        print('elapsed time: ', self.elapsed_time)

        self.make_output_file()

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

        for row_index_m1 in range(start, end):
            row = []
            for col_index_m2 in range(self.matrix_2.col_size):
                product = sum(
                    [
                        self.matrix_1.rows[row_index_m1][col_index_m1] *
                        self.matrix_2.get_col(col_index_m2)[row_index_m1]
                        for col_index_m1 in range(self.matrix_1.col_size)
                    ]
                )
                row.append(product)
            thread_result.append(row)

        return thread_result

    def get_multi_matrix(self):
        if self.matrix_1.col_size != self.matrix_2.row_size:
            raise ValueError("O número de colunas da matriz 1 deve ser igual ao número de linhas da matriz 2!")

        global_result = []
        threads_list = []
        chunks = self._get_chunks(self.matrix_1.row_size, THREADS_AMOUNT)

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
                     f'{self.matrix_1.col_size} x {self.matrix_2.row_size} - [{THREADS_AMOUNT} THR] [{self.elapsed_time}].txt')

        with open(file_name, 'w') as file:
            file.write(f'{self.matrix_1.col_size} {self.matrix_2.row_size}\n')
            for row in self.result:
                line = ' '.join(map(str, row))
                file.write(line + '\n')


if __name__ == '__main__':
    MethodTwo()
