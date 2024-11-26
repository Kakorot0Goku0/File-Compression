#include <math.h>
#include <stdlib.h>

#define PI 3.14159265358979323846

#ifdef _WIN32
#define EXPORT __declspec(dllexport)
#else
#define EXPORT
#endif

EXPORT void dct2(double *input, double *output, int M, int N) {
    // ... (rest of the function remains the same)
     for (int u = 0; u < M; u++) {
        for (int v = 0; v < N; v++) {
            double sum = 0.0;
            for (int i = 0; i < M; i++) {
                for (int j = 0; j < N; j++) {
                    double cos_term = cos((2*i + 1) * u * PI / (2*M)) * cos((2*j + 1) * v * PI / (2*N));
                    sum += input[i*N + j] * cos_term;
                }
            }
            double cu = (u == 0) ? 1/sqrt(2) : 1;
            double cv = (v == 0) ? 1/sqrt(2) : 1;
            output[u*N + v] = (2.0 / sqrt(M*N)) * cu * cv * sum;
        }
    }
}

EXPORT void idct2(double *input, double *output, int M, int N) {
    // ... (rest of the function remains the same)
    for (int i = 0; i < M; i++) {
        for (int j = 0; j < N; j++) {
            double sum = 0.0;
            for (int u = 0; u < M; u++) {
                for (int v = 0; v < N; v++) {
                    double cu = (u == 0) ? 1/sqrt(2) : 1;
                    double cv = (v == 0) ? 1/sqrt(2) : 1;
                    double cos_term = cos((2*i + 1) * u * PI / (2*M)) * cos((2*j + 1) * v * PI / (2*N));
                    sum += cu * cv * input[u*N + v] * cos_term;
                }
            }
            output[i*N + j] = (2.0 / sqrt(M*N)) * sum;
        }
    }
}