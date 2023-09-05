from matrix import Matrix
import os
import time

current_dir = os.path.dirname(os.path.realpath(__file__))

# noinspection DuplicatedCode
class MethodOne:
    def __init__(self):
        self.matrix_1 = Matrix(f'{current_dir}/src/10_int.txt')
        self.matrix_2 = Matrix(f'{current_dir}/src/10_int.txt')

        start_time = time.time()
        self.result = self.get_multi_matrix()
        end_time = time.time()

        self.elapsed_time = end_time - start_time
        self.elapsed_time = '{:.5f}'.format(self.elapsed_time)

        print('result: ', self.result)
        print('elapsed time: ', self.elapsed_time)

        self.make_output_file()

    def get_multi_matrix(self):
        if self.matrix_1.col_size != self.matrix_2.row_size:
            raise ValueError("O número de colunas da matriz 1 deve ser igual ao número de linhas da matriz 2!")

        result = []
        for row_index_m1 in range(self.matrix_1.row_size):
            row = []
            for col_index_m2 in range(self.matrix_2.col_size):
                product = sum(
                    [
                        self.matrix_1.rows[row_index_m1][col_index_m1] *
                        self.matrix_2.get_col(col_index_m2)[col_index_m1]
                        for col_index_m1 in range(self.matrix_1.col_size)
                    ]
                )
                row.append(product)
            result.append(row)

        return result

    def make_output_file(self):
        file_name = f'output/matriz {self.matrix_1.col_size} x {self.matrix_2.row_size} - [{self.elapsed_time}].txt'

        with open(file_name, 'w') as file:
            file.write(f'{self.matrix_1.col_size} {self.matrix_2.row_size}\n')
            for row in self.result:
                line = ' '.join(map(str, row))
                file.write(line + '\n')


if __name__ == '__main__':
    MethodOne()
