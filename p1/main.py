from matrix import Matrix
import os
import time

current_dir = os.path.dirname(os.path.realpath(__file__))
parent_dir = os.path.dirname(current_dir)


class MethodOne:
    def __init__(self):
        self.matrix_1 = Matrix(f'{parent_dir}/src/10_int.txt')
        self.matrix_2 = Matrix(f'{parent_dir}/src/10_int.txt')

        start_time = time.time()
        self.result = self.get_multi_matrix()
        end_time = time.time()

        elapsed_time = end_time - start_time

        print('result: ', self.result)
        print('elapsed time: ', '{:.5f}'.format(elapsed_time))

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


if __name__ == '__main__':
    MethodOne()
