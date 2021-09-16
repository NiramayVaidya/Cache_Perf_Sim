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

vector<int> gather(vector< vector<int> > A, vector< vector<int> > indices) {
	int n = A.size();

	// initialise B with 0s
	vector<int> B(n, 0);

	for (int i = 0; i < n; i++) {
		// B[i] = A[indices[i][0]][indices[i][1]];
		// B[i] = A[i][i];
		B[i] = A[0][i];
	}

	return B;
}

vector< vector<int> > getIndices(int n) {
	vector<int> tmp(2, 0);
	vector< vector<int> > indices(n, tmp);
	for (int i = 0; i < n; i++) {
		indices[i][0] = indices[i][1] = i;
		// indices[i][0] = 0;
		// indices[i][1] = i;
	}
	return indices;
}

void printVector(vector<int> vec) {
	vector<int>::iterator it;
	for (it = vec.begin(); it != vec.end(); it++) {
			cout << *it;
			cout << "\t";
	}
	cout << endl;
}

int main (int argc, char* argv[]) {
	string filename;
	if (argc < 3) {
		filename = "2000.in";
	} else {
		filename = argv[2];
	}
	vector< vector<int> > A = read(filename);
	vector< vector<int> > indices = getIndices(A.size());
    parsec_roi_begin();
	vector<int> B = gather(A, indices);
    parsec_roi_end();
	// printVector(B);
	return 0;
}
