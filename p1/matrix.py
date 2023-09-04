# noinspection PyMethodMayBeStatic
class Matrix:
    def __init__(self, matrix_path):
        self.row_size, self.col_size, self.rows = self.__load_matrix(matrix_path)
        # print('matrix:', self.rows)

    def __load_matrix(self, matrix_path) -> object:
        with open(matrix_path, 'r') as file:
            lines = [[int(val) for val in line.strip().split()] for line in file]
            return lines[0][0], lines[0][1], lines[1:]

    def get_col(self, col_index):
        col = [row[col_index] for row in self.rows]
        return col

