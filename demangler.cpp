#include <cxxabi.h>
#include <iostream>

using namespace std;

int main(int argc, char* argv[]) {
  int status;
  if(argc < 2) return 1;
  cout << abi::__cxa_demangle(argv[1], nullptr, nullptr, &status );
  return 0;
}
