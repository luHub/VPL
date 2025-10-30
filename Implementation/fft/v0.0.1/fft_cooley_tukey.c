

typedef struct {
    double re;
    double im;
} complex_t;


complex_t c_add(complex_t a, complex_t b) {
    complex_t r = {a.re + b.re, a.im + b.im};
    return r;
}


complex_t c_sub(complex_t a, complex_t b) {
    complex_t r = {a.re - b.re, a.im - b.im};
    return r;
}


complex_t c_mul(complex_t a, complex_t b) {
    complex_t r = {
        a.re * b.re - a.im * b.im,
        a.re * b.im + a.im * b.re
    };
    return r;
}


complex_t twiddle(int k, int N) {
    double angle = -2.0 * M_PI * k / (double)N;
    complex_t w = {cos(angle), sin(angle)};
    return w;
}


void FFT_CooleyTukey(complex_t* x, int N) {
    if (N <= 1) return;

    int half = N / 2;

    
    complex_t* even = (complex_t*) malloc(half * sizeof(complex_t));
    complex_t* odd  = (complex_t*) malloc(half * sizeof(complex_t));

    for (int i = 0; i < half; i++) {
        even[i] = x[2*i];
        odd[i]  = x[2*i + 1];
    }

    
    FFT_CooleyTukey(even, half);
    FFT_CooleyTukey(odd, half);

    
    for (int k = 0; k < half; k++) {
        complex_t t = c_mul(twiddle(k, N), odd[k]);
        x[k]       = c_add(even[k], t);
        x[k+half]  = c_sub(even[k], t);
    }

    free(even);
    free(odd);
}


void print_fft(complex_t* x, int N) {
    for (int i = 0; i < N; i++) {
        printf("%d: %.4f + %.4fi\n", i, x[i].re, x[i].im);
    }
}


int main() {
    int N = 8;
    complex_t x[8];

    
    for (int i = 0; i < N; i++) {
        x[i].re = sin(2*M_PI*i/N);
        x[i].im = 0.0;
    }

    printf("Input:\n");
    print_fft(x, N);

    FFT_CooleyTukey(x, N);

    printf("\nFFT Output:\n");
    print_fft(x, N);

    return 0;
}

