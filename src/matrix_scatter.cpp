#include <sstream>
#include <string>
#include <fstream>
#include <iostream>
#include <vector>
// #include <boost/algorithm/string.hpp>

using namespace std;
// using namespace boost::algorithm;

vector< vector<int> > indices;

void parsec_roi_begin() {

}

void parsec_roi_end() {

}

vector<int> read(string filename) {
	vector<int> A;
	string line;
	ifstream infile;
	infile.open (filename.c_str());

	while (getline(infile, line) && !line.empty()) {
		// requires a vector of strings, then need to do atoi for every access in A
		// split(A, line, boost::is_any_of("\t"));
		istringstream iss(line);
		int a, j = 0;
		while (iss >> a) {
			A.push_back(a);
			j++;
		}
	}

	infile.close();
	return A;
}

vector< vector<int> > scatter(vector<int> A, vector< vector<int> > indices) {
	int n = A.size();

	// initialise B with 0s
	vector<int> tmp(n, 0);
	vector< vector<int> > B(n, tmp);

	for (int i = 0; i < n; i++) {
		// B[indices[i][0]][indices[i][1]] = A[i];
		// B[n - 1][i] = A[i];
		B[i][n - 1 - i] = A[i];
	}

	return B;
}

vector< vector<int> > getIndices(int n) {
	vector<int> tmp(2, 0);
	vector< vector<int> > indices(n, tmp);
	for (int i = 0; i < n; i++) {
		indices[i][0] = i;
		indices[i][1] = n - 1 - i;
		// indices[i][0] = n - 1;
		// indices[i][1] = i;
	}
	return indices;
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
	vector<int> A = read(filename);
	vector< vector<int> > indices = getIndices(A.size());
    parsec_roi_begin();
	vector< vector<int> > B = scatter(A, indices);
    parsec_roi_end();
	// printMatrix(B);
	return 0;
}
