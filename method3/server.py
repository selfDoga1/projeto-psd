from dotenv import load_dotenv
import Pyro4
import os

DEBUG = True
load_dotenv()


# noinspection PyMethodMayBeStatic,DuplicatedCode

class Server:

    remote_workers = {}
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
        return 'the process is prepared!'

    @classmethod
    @Pyro4.expose
    def start(cls):
        index = 0
        for worker_id in cls.remote_workers:
            worker = cls.remote_workers[worker_id]
            worker['result'] = worker['object'].work(cls.matrix_1, cls.matrix_2, cls.chunks[index])
            index += 1
        print(cls.remote_workers)

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
