
int Fibon(int n) {
    // Base case: return 1 for the first and second Fibonacci numbers
    if ((n == 1) || (n == 2)) {
        return 1;
    }
    // Recursive case: sum of the two preceding Fibonacci numbers
    return Fibon(n - 1) + Fibon(n - 2);
}
