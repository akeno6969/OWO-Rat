#include <iostream>
#include <fstream>

using namespace std;

int main() {
    ifstream logFile("owokeylog.txt");

    if (!logFile.is_open()) {
        cerr << "Failed to open the log file!" << endl;
        return -1;
    }

    string line;
    while (getline(logFile, line)) {
        cout << line << endl;
    }

    logFile.close();
    return 0;
}