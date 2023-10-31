### Calculating C, A, t1 and t2 for K pool and Curve fit
import numpy as np


def func_CAt1t2(a, b, r):
    C = np.sqrt(-4 * a * b + (a + b + a * r) ** 2)
    A = -(a - b + a * r - C) / (2 * C)
    t1 = 2 / (a + b + a * r + C)
    t2 = 2 / (a + b + a * r - C)
    return C, A, t1, t2


### Optimized K Pool
def func_kpool(t, a, b, r):
    C, A, t1, t2 = func_CAt1t2(a, b, r)
    yy = 1 - A * np.exp(-t / t1) - (1 - A) * np.exp(-t / t2)
    return yy


### Curve fitting
def func_pulse(t, a, b, r, tp):
    C, A, t1, t2 = func_CAt1t2(a, b, r)
    yy = -np.exp(-t / tp) * (-(A * t1) / (t1 - tp) + (t2 * (A - 1.0)) / (t2 - tp) + 1.0) + np.exp(-t / tp) * (
            np.exp(t / tp) - (A * t1 * np.exp(-t / t1 + t / tp)) / (t1 - tp) + (
            t2 * np.exp(-t / t2 + t / tp) * (A - 1.0)) / (t2 - tp))
    return yy