from matrix import MatrixSerializer
from dotenv import load_dotenv
from Pyro4.core import Daemon
from threading import Thread
import Pyro4
import os
import time
import numpy as np

DEBUG = True
load_dotenv()
THREADS_AMOUNT = 2


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


# noinspection DuplicatedCode
class CustomDaemon(Daemon):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @staticmethod
    def serveSimple(objects, host=None, port=0, daemon=None, ns=True, verbose=True, server_uri=None):
        if daemon is None:
            daemon = Daemon(host, port)
        with daemon:
            for obj, name in objects.items():
                localname = name
                uri = daemon.register(obj, localname)
                server = Pyro4.core.Proxy(server_uri)
                print(f'{server.register_remote_worker(uri, server_uri)}')
                print("Worker is running.")
            daemon.requestLoop()


# noinspection DuplicatedCode
class Worker:
    thread_per_chunk = []
    matrix_1 = None
    matrix_2 = None

    @classmethod
    @Pyro4.expose
    def work(cls, matrix_1, matrix_2, worker_chunk, worker_id):
        cls.matrix_1 = MatrixSerializer().deserialize(matrix_1)
        cls.matrix_2 = MatrixSerializer().deserialize(matrix_2)

        worker_chunk_start, worker_chunk_end = worker_chunk[0], worker_chunk[1]
        chunk_per_thread = cls.__get_chunk_per_thread(worker_chunk_start, worker_chunk_end)

        worker_result = []

        for chunk in chunk_per_thread:
            thread = CustomThread(target=cls.__process, args=[chunk[0], chunk[1]])
            cls.thread_per_chunk.append(thread)

        start_time = time.time()

        for thread in cls.thread_per_chunk:
            thread.start()

        for thread in cls.thread_per_chunk:
            worker_result.extend(thread.join())

        end_time = time.time()
        elapsed_time = end_time - start_time

        return (
            worker_result,
            elapsed_time,
            THREADS_AMOUNT,
            worker_id
        )

    @classmethod
    def __get_chunk_per_thread(cls, worker_chunk_start, worker_chunk_end):
        interval_size = (worker_chunk_end - worker_chunk_start) // THREADS_AMOUNT
        interval_per_thread = []

        if interval_size == 0:
            interval_per_thread.append([worker_chunk_start, worker_chunk_end])
        else:
            for i in range(THREADS_AMOUNT):
                start = i * interval_size
                end = (i + 1) * interval_size if i < THREADS_AMOUNT - 1 else worker_chunk_end
                interval_per_thread.append([start, end])

        return interval_per_thread

    @classmethod
    def __process(cls, start, end):
        worker_result = []
        # for row_index_m1 in range(start, end):
        #     row = []
        #     for col_index_m2 in range(cls.matrix_2.col_size):
        #         product = sum(
        #             [
        #                 cls.matrix_1.rows[row_index_m1][col_index_m1] *
        #                 cls.matrix_2.get_col(col_index_m2)[col_index_m1]
        #                 for col_index_m1 in range(cls.matrix_1.col_size)
        #             ]
        #         )
        #         row.append(product)
        #     worker_result.append(row)

        array_matrix_1 = np.array(cls.matrix_1.rows)
        array_matrix_2 = np.array(cls.matrix_2.rows)

        sub_matrix_1 = array_matrix_1[start:end]
        sub_matrix_2 = array_matrix_2

        sub_result = np.dot(sub_matrix_1, sub_matrix_2.T)

        for row in sub_result:
            worker_result.append(row.tolist())

        return worker_result


if __name__ == "__main__":
    Pyro4.config.SERIALIZER = os.getenv('SERIALIZER')
    server_uri = f'PYRO:{os.getenv("SERVER_NAME")}@{os.getenv("SERVER_HOST")}:{os.getenv("SERVER_PORT")}'

    CustomDaemon().serveSimple(
        {Worker: f'{os.getenv("WORKER_NAME")}'},
        host=os.getenv('WORKER_HOST'),
        port=0,
        server_uri=server_uri
    )
