#include"LeakDetector.h"

int main() {
	int* a = new int;
	int* b = new int[12];
	delete a;
	delete[]b;
	return 0;
}