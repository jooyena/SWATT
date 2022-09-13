from typing import List
import serial
import numpy
import random
import time

PORT = 'COM8'
BaudRate = 9600

rows = 41
cols = 256
memory_size = 10000
stream_size = 256
seed_size = 20
Mem = [0 for i in range(0, memory_size)]
arduino = serial.Serial(PORT, BaudRate)

rc4: List[int] = [0 for j in range(0, stream_size)]
seed = [0 for k in range(0, seed_size)]

INT_BITS = 8


def leftRotate(n, d):
    return numpy.short(n << d) | numpy.short(n >> (INT_BITS - d))


def RC4():
    s = [0 for i in range(0, stream_size)]
    j = 0

    for i in range(0, stream_size):
        s[i] = i % 256
        rc4[i] = seed[i % seed_size]

    for i in range(0, stream_size):
        j = (j + s[i] + rc4[i]) % stream_size
        s[i], s[j] = s[j], s[i]

    i = j = 0

    for k in range(0, stream_size):
        i = (i + 1) % stream_size
        j = (j + s[i]) % stream_size
        s[i], s[j] = s[j], s[i]
        rc4[i] = s[(s[i] + s[j]) % stream_size]


def verifier():
    C = [0 for k in range(0, 8)]
    j = 0

    for k in range(0, rows):
        RC4()

        for i in range(1, cols):
            address = abs(numpy.short(rc4[i] << 8) + C[j - 1]) % memory_size
            C[j] = (C[j] + rc4[i - 1] + (Mem[address] | C[abs(j - 2) % 8])) % stream_size
            C[j] = leftRotate(C[j], 1) % stream_size
            j = (j + 1) % 8
    return C


def pull_memory():
    print("pull_memory")

    for i in range(-1, memory_size):
        # print(i)
        buff = arduino.readline().strip()

        if len(buff) > 4:
            print("error!")
            continue

        else:
            Mem[i] = int(buff.decode())

    return Mem


def main():
    # set up
    C = [0 for i in range(0, 8)]
    TIME = 0
    for i in range(0, seed_size):
        seed[i] = i

    while True:
        # arduino.write([seed[0], seed[1], seed[2], seed[3], seed[4]])
        pull_memory()
        print(Mem)
        V = verifier()
        if arduino.readable():
            for i in range(0, 8):
                buff = arduino.readline().strip()
                C[i] = int(buff.decode())
            buff = arduino.readline().strip()
            TIME = int(buff.decode())

        if TIME > 1100:
            print(str(TIME)+"초 걸림 "+"Time out!")
            break

        if V == C:
            print("Success")
        else:
            print("fails")
            print(V)
            print(C)

        break


if __name__ == '__main__':
    main()
