import Pyro4


# noinspection PyMethodMayBeStatic,DuplicatedCode
class Matrix:
    def __init__(self, matrix_path=None, row_size=None, col_size=None, rows=None):
        if matrix_path:
            self.row_size, self.col_size, self.rows = self.__load_matrix(matrix_path)
        else:
            self.row_size = row_size
            self.col_size = col_size
            self.rows = rows

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

    def get_serialized(self):
        return MatrixSerializer().serializer(self)

    def __repr__(self):
        return f'Matrix: {self.row_size} rows and {self.col_size} cols'


# noinspection PyMethodMayBeStatic
class MatrixSerializer(Pyro4.util.SerializerBase):
    def serializer(self, obj: Matrix) -> object:
        if isinstance(obj, Matrix):
            return obj.row_size, obj.col_size, obj.rows
        else:
            raise TypeError("Can only serialize Person objects")

    def deserialize(self, obj):
        row_size, col_size, rows = obj
        return Matrix(row_size=row_size, col_size=col_size, rows=rows)