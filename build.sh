#!/bin/sh
g++ -I ./src -o ./gdecode.exe ./src/gdecode.cpp 
g++ -o ./intrcon.exe ./src/intrcon.cpp
g++ -o ./intr_fdma.exe ./src/intr_fdma.cpp
g++ -o ./fdma.exe ./src/fdma.cpp -lrt -lpthread -lpigpio
g++ -o ./place.exe ./src/place.cpp -lrt -lpthread -lpigpio

