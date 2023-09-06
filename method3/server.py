from dotenv import load_dotenv
import Pyro4
import os

DEBUG = True
load_dotenv()


# noinspection PyMethodMayBeStatic,DuplicatedCode
class CentralServer:
    def __init__(self):
        self.remote_workers = {}
        self.matrix_1 = []
        self.matrix_2 = []
        self.chunks = []
        self.result = []
        self.workers_initiated = False

    @Pyro4.expose
    def register_worker(self, worker_uri, worker_id):
        worker = Pyro4.Proxy(worker_uri)
        self.remote_workers[worker_id] = {
            'object': worker,
            'result': None
        }
        print('-- register_worker --')
        print(f'worker registered with id {worker_id}!')

    @Pyro4.expose
    def register_matrices(self, matrix_1, matrix_2):
        self.matrix_1 = matrix_1
        self.matrix_2 = matrix_2

        print('-- register_matrices --')
        print(self.matrix_1, ' - ', self.matrix_2)

    @Pyro4.expose
    def prepare(self):
        row_size, col_size, rows = self.matrix_1
        self.chunks = self.__divide_chunks_per_worker(row_size, len(self.remote_workers))

    @Pyro4.expose
    def start(self):
        index = 0
        for worker_id in self.remote_workers:
            worker = self.remote_workers[worker_id]
            worker['result'] = worker['object'].work(self.matrix_1, self.matrix_2, self.chunks[index], worker_id)
            index += 1

    def __divide_chunks_per_worker(self, rows, workers_amount):
        result = []
        chunk_per_worker = rows // workers_amount
        rest_division = rows % workers_amount
        start = 0

        for i in range(workers_amount):
            end = start + chunk_per_worker
            if i < rest_division:
                end += 1
            result.append([start, end])
            start = end

        return result


if __name__ == '__main__':
    Pyro4.config.HOST = os.getenv('HOST')
    Pyro4.config.SERIALIZER = os.getenv('SERIALIZER')
    daemon = Pyro4.Daemon()
    uri = daemon.register(CentralServer)
    ns = Pyro4.locateNS()
    ns.register('server', uri)

    print('Central Server ready. uri:', uri)
    daemon.requestLoop()
