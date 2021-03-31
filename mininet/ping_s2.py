import os
import time

L = []

def send(L):
    interval = float(L[0])
    size = float(L[1])
    time.sleep(interval)
    command = "ping -c 1 -s "+str(size)+" 10.0.0.33"
    print(command)
    os.system(command)

if __name__ == '__main__':
    with open('base_B_0901_v2.txt', 'r') as f:
        for line in f:
            for Word in line.split():
                L.append(Word)

            send(L)
            del L[:]


