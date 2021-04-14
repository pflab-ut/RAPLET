SHELL=/bin/bash
C_DIR=$(shell pwd)

lhook.so: hook_libroscpp.cpp demangler
	g++ -g -Wall -shared -fPIC -pthread -ldl -I/opt/ros/melodic/include -I$(C_DIR)/devel/include hook_libroscpp.cpp -o lhook.so

demangler: demangler.cpp
	g++ -o demangler demangler.cpp

clean_pl_data:
	rm ~/.ros/raplet/log*
