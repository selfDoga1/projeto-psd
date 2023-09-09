from dotenv import load_dotenv
from threading import Thread
import Pyro4
import os
import time
from datetime import datetime

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
        current_time = datetime.now().strftime("%H:%M:%S")
        matrix_1_col_size = cls.matrix_1[0]
        matrix_2_row_size = cls.matrix_1[1]
        global_result = []
        global_log = {}

        if matrix_1_col_size != matrix_2_row_size:
            raise ValueError("O número de colunas da matriz 1 deve ser igual ao número de linhas da matriz 2!")

        index = 0
        for worker_id in cls.remote_workers:
            worker = cls.remote_workers[worker_id]['object']
            thread = CustomThread(target=worker.work, args=[cls.matrix_1, cls.matrix_2, cls.chunks[index], worker_id])
            cls.thread_per_worker.append(thread)
            index += 1

        start_time = time.time()

        for thread in cls.thread_per_worker:
            thread.start()

        for thread in cls.thread_per_worker:
            worker_result, worker_elapsed_time, worker_threads_amount, worker_id = thread.join()
            global_result.extend(worker_result)
            global_log[f'{worker_id}'] = {
                'threads_amount': worker_threads_amount,
                'elapsed_time': worker_elapsed_time
            }

        end_time = time.time()
        elapsed_time = end_time - start_time

        cls.make_log_file(global_log, elapsed_time, current_time)
        return global_result, len(cls.remote_workers), elapsed_time, current_time

    @staticmethod
    def divide_chunks_per_worker(rows, workers_amount):
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

    @classmethod
    def make_log_file(cls, global_log, elapsed_time, current_time):
        file_name = (
            f'output/log [{current_time}] '
            f'{cls.matrix_1[0]} x {cls.matrix_2[1]} - '
            f'[{len(cls.remote_workers)} WORKERS] [{elapsed_time}].txt'
        )

        with open(file_name, 'w') as file:
            for worker_uri in global_log:
                worker = global_log[worker_uri]
                line = f'{worker_uri}: {worker["threads_amount"]} threads - elapsed time: {worker["elapsed_time"]}'
                file.write(line + '\n')


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
