from dotenv import load_dotenv
from threading import Thread
import Pyro4
import os
import time

DEBUG = True
load_dotenv()


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


# noinspection PyMethodMayBeStatic,DuplicatedCode

class Server:

    remote_workers = {}
    thread_per_worker = []
    matrix_1 = []
    matrix_2 = []
    chunks = []
    result = []
    workers_initiated = False

    @classmethod
    @Pyro4.expose
    def register_remote_worker(cls, worker_uri, server_uri):
        try:
            worker = Pyro4.Proxy(worker_uri)
            cls.remote_workers[worker_uri] = {
                'object': worker,
                'result': None
            }

            print(f'Worker registered with uri: {worker_uri}!')
            return f'Worker registered on Server {server_uri} with uri: {worker_uri}!'
        except Exception as e:
            return e

    @classmethod
    @Pyro4.expose
    def show_remote_workers(cls):
        return f'{cls.remote_workers.keys()}'

    @classmethod
    @Pyro4.expose
    def register_matrices(cls, matrix_1, matrix_2):
        cls.matrix_1 = matrix_1
        cls.matrix_2 = matrix_2
        return 'matrices registered!'

    @classmethod
    @Pyro4.expose
    def prepare(cls):
        row_size, col_size, rows = cls.matrix_1
        cls.chunks = cls.divide_chunks_per_worker(row_size, len(cls.remote_workers))
        print('chunks', cls.chunks)
        return 'the process is prepared!'

    @classmethod
    @Pyro4.expose
    def start(cls):
        matrix_1_col_size = cls.matrix_1[0]
        matrix_2_row_size = cls.matrix_1[1]
        print('matrix_1_col_size:', matrix_1_col_size)
        print('matrix_2_row_size:', matrix_2_row_size)
        global_result = []

        if matrix_1_col_size != matrix_2_row_size:
            raise ValueError("O número de colunas da matriz 1 deve ser igual ao número de linhas da matriz 2!")

        index = 0
        for worker_id in cls.remote_workers:
            worker = cls.remote_workers[worker_id]['object']
            thread = CustomThread(target=worker.work, args=[cls.matrix_1, cls.matrix_2, cls.chunks[index]])
            cls.thread_per_worker.append(thread)
            index += 1

        start_time = time.time()

        for thread in cls.thread_per_worker:
            thread.start()

        for thread in cls.thread_per_worker:
            worker_result, worker_elapsed_time = thread.join()
            global_result.extend(worker_result)

        end_time = time.time()
        elapsed_time = end_time - start_time

        return global_result, len(cls.remote_workers), elapsed_time

    @staticmethod
    def divide_chunks_per_worker(rows, workers_amount):
        _result = []
        chunk_per_worker = rows // workers_amount
        rest_division = rows % workers_amount
        start = 0

        for i in range(workers_amount):
            end = start + chunk_per_worker
            if i < rest_division:
                end += 1
            _result.append([start, end])
            start = end

        return _result




if __name__ == '__main__':
    Pyro4.config.SERIALIZER = os.getenv('SERIALIZER')

    daemon = Pyro4.Daemon.serveSimple({
        Server: os.getenv('SERVER_NAME'),
    },
        host=os.getenv('SERVER_HOST'),
        port=int(os.getenv('SERVER_PORT')),
        ns=False,
        verbose=True
    )

    daemon.requestLoop()
