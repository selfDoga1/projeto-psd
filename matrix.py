# noinspection PyMethodMayBeStatic
class Matrix:
    def __init__(self, matrix_path):
        self.row_size, self.col_size, self.rows = self.__load_matrix(matrix_path)
        # print('matrix:', self.rows)
        print(self.row_size, self.col_size)

    def __load_matrix(self, matrix_path) -> object:
        with open(matrix_path, 'r') as file:
            matrix = file.readlines()
            matrix_size = matrix[0].split()
            matrix_lines = matrix[1:]
            matrix = [[float(val) for val in line.strip().split()] for line in matrix_lines]
            return int(matrix_size[0]), int(matrix_size[1]), matrix

    def get_col(self, col_index):
        col = [row[col_index] for row in self.rows]
        return col

