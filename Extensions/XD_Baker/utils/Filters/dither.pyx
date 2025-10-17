import numpy as np
cimport numpy as np

def floyd_steinberg(np.ndarray[np.float64_t, ndim=3] image, int shagreen):
    cdef int Lx = image.shape[0]
    cdef int Ly = image.shape[1]
    cdef int Lc = image.shape[2]
    cdef int i, j, c
    cdef double rounded, quant_error
    cdef int sixteen = 16

    for j in range(Ly):
        for i in range(Lx):
            for c in range(Lc):
                rounded = round(image[i, j, c] * shagreen) / shagreen
                quant_error = image[i, j, c] - rounded
                image[i, j, c] = rounded

                if i < Lx - 1:
                    image[i + 1, j, c] += quant_error * 7 / sixteen
                if i > 0 and j < Ly - 1:
                    image[i - 1, j + 1, c] += quant_error * 3 / sixteen
                if j < Ly - 1:
                    image[i, j + 1, c] += quant_error * 5 / sixteen
                if i < Lx - 1 and j < Ly - 1:
                    image[i + 1, j + 1, c] += quant_error * 1 / sixteen

    return image