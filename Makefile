CC = clang++

ATTACKS_PATH = ./attacks
P_ORACLE_PATH = $(ATTACKS_PATH)/padding_oracle

all: main

main: main.cc $(P_ORACLE_PATH)/p_oracle.o
	$(CC) main.cc  $(P_ORACLE_PATH)/p_oracle.o -o main

p_oracle.o: $(P_ORACLE_PATH)/p_oracle.cc

clean:
	rm -f main $(P_ORACLE_PATH)/p_oracle.o
