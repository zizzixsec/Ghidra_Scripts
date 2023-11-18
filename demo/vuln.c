#include <stdio.h>

void vuln() {
    char name[200];
    puts("Hello! What is your name? ");
    gets(name);
    printf(name);
}

int main(int argc, char** argv) {
    vuln();
    return 0;
}
