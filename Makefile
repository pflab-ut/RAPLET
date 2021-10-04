SHELL=/bin/bash
C_DIR=$(shell pwd)

all: lhook.so

log_file:
	mkdir -p ~/.ros/raplet

lhook.so: hook_libroscpp.cpp demangler log_file
	g++ -g -Wall -shared -fPIC -pthread -ldl -I/opt/ros/noetic/include -I$(C_DIR)/devel/include hook_libroscpp.cpp -o lhook.so

demangler: demangler.cpp
	g++ -o demangler demangler.cpp

clean_log:
	rm ~/.ros/raplet/log*

clean:
	rm *.o demangler lhook.so

.PHONY: clean_pl_data clean all
