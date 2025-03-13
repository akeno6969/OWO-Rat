#include <iostream>
#include <Windows.h>

using namespace std;

int main() {
    HHOOK hook = GetCurrentHook();

    if (hook == NULL) {
        cerr << "No active keylogger hook found!" << endl;
        return -1;
    }

    if (UnhookWindowsHookEx(hook)) {
        cout << "Keylogger stopped successfully!" << endl;
    } else {
        cerr << "Failed to stop the keylogger!" << endl;
        return -1;
    }

    return 0;
}