#include <sstream>
#include <string>
#include <fstream>
#include <iostream>
#include <vector>

using namespace std;

void parsec_roi_begin() {

}

void parsec_roi_end() {

}

vector< vector<int> > read(string filename) {
	vector< vector<int> > A;
	string line;
	ifstream infile;
	infile.open (filename.c_str());

	int i = 0;
	while (getline(infile, line) && !line.empty()) {
		istringstream iss(line);
		A.resize(A.size() + 1);
		int a, j = 0;
		while (iss >> a) {
			A[i].push_back(a);
			j++;
		}
		i++;
	}

	infile.close();
	return A;
}

vector< vector<int> > colwise_copy(vector< vector<int> > A) {
	int n = A.size();

	// initialise B with 0s
	vector<int> tmp(n, 0);
	vector< vector<int> > B(n, tmp);

	for (int i = 0; i < n; i++) {
		for (int j = 0; j < n; j++) {
			B[j][i] = A[j][i];
		}
	}
	return B;
}

void printMatrix(vector< vector<int> > matrix) {
	vector< vector<int> >::iterator it;
	vector<int>::iterator inner;
	for (it = matrix.begin(); it != matrix.end(); it++) {
		for (inner = it->begin(); inner != it->end(); inner++) {
			cout << *inner;
			if (inner + 1 != it->end()) {
				cout << "\t";
			}
		}
		cout << endl;
	}
}

int main (int argc, char* argv[]) {
	string filename;
	if (argc < 3) {
		filename = "2000.in";
	} else {
		filename = argv[2];
	}
    parsec_roi_begin();
	vector< vector<int> > B = colwise_copy(read(filename));
    parsec_roi_end();
	printMatrix(B);
	return 0;
}
