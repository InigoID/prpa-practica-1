from multiprocessing import Process, Semaphore, current_process, Value, Array
from time import sleep
import random

N = 4
NPROD = 5
BUFFER_SIZE = 3

def add_data(buffer, pid, data): 
    buffer[pid] = data

def get_data(buffer):
    other = [0] * len(buffer)
    maximum = max(buffer)
    for i in range(len(buffer)):
        if buffer[i] == -1:
            other[i] = maximum + 1
        else:
            other[i] = buffer[i]
    min_buffer = other[0]
    position = 0
    for i in range(1, len(other)):
        if other[i] < min_buffer and other[i] != -1:
            min_buffer = other[i]
            position = i
    return min_buffer, position

def producer(buffer, pid, sem_empty, sem_full, running, N_prod):
    v = random.randint(0, 5)
    while running[pid]:
        print(f"productor {current_process().name} produce")
        sleep(random.random() / 3)
        v += random.randint(0, 5)
        sem_empty[pid].acquire()
        add_data(buffer, pid, v)
        print(f"productor {current_process().name} almacena {v}")
        sem_full[pid].release()
        N_prod[pid] -= 1
        if N_prod[pid] == 0:
            buffer[pid] = -1
            running[pid] = 0
            print(f"productor {current_process().name} acaba")

def consumer(buffer, sem_empty, sem_full, running, result):
    for i in range(NPROD):
        sem_full[i].acquire()
    while 1 in running:
        print(f"consumidor {current_process().name} desalmacena")
        data, position = get_data(buffer)
        sem_empty[position].release()
        print(f"consumidor {current_process().name} consume {data}")
        result.append(data)
        sleep(random.random() / 3)
        sem_full[position].acquire()
    print(f"{current_process().name} no puede consumir, todos los productores han acabado")
    print("Lista final:", result)

def main():
    buffer = Array('i', [-1] * (NPROD * BUFFER_SIZE))
    running = Array('i', NPROD)
    N_prod = Array('i', NPROD)
    for i in range(NPROD):
        running[i] = 1
        N_prod[i] = N

    sem_empty_arr = []
    sem_full_arr = []
    for i in range(NPROD):
        empty_arr = Semaphore(BUFFER_SIZE)
        full_arr = Semaphore(0)
        sem_empty_arr.append(empty_arr)
        sem_full_arr.append(full_arr)

    result = []
    consumer_list = [Process(target=consumer,
                            name="cons",
                            args=(buffer, sem_empty_arr, sem_full_arr, running, result))]

    producer_list = [Process(target=producer,
                            name=f'prod_{i}',
                            args=(buffer, i, sem_empty_arr, sem_full_arr, running, N_prod))
                    for i in range(NPROD)]

    for p in producer_list + consumer_list:
        p.start()

    for p in producer_list + consumer_list:
        p.join()

if __name__ == "__main__":
    main()
