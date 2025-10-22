// floyd_steinberg.cpp
#include <iostream>
#include <cmath>
#include <cassert>

extern "C" __declspec(dllexport)
void floyd_steinberg(double* image, int Lx, int Ly, int Lc, float threshold) {
    // Проверяем корректность входных параметров
    assert(Lx > 0 && Ly > 0 && Lc > 0);
    assert(threshold > 0);
    
    const float error_factors[4] = {7.0f/16.0f, 3.0f/16.0f, 5.0f/16.0f, 1.0f/16.0f};
    
    for (int j = 0; j < Ly; j++) {
        for (int i = 0; i < Lx; i++) {
            for (int c = 0; c < Lc; c++) {
                int idx = (j * Lx + i) * Lc + c;
                float old_pixel = image[idx];
                
                // Квантование с проверкой границ
                float rounded = std::round(old_pixel * threshold) / threshold;
                rounded = std::max(0.0f, std::min(rounded, 1.0f)); // Ограничиваем диапазон
                
                float quant_error = old_pixel - rounded;
                image[idx] = rounded;

                // Распространение ошибки с проверкой границ
                if (i + 1 < Lx)
                    image[(j * Lx + (i + 1)) * Lc + c] += quant_error * error_factors[0];
                if (i > 0 && j + 1 < Ly)
                    image[((j + 1) * Lx + (i - 1)) * Lc + c] += quant_error * error_factors[1];
                if (j + 1 < Ly)
                    image[((j + 1) * Lx + i) * Lc + c] += quant_error * error_factors[2];
                if (i + 1 < Lx && j + 1 < Ly)
                    image[((j + 1) * Lx + (i + 1)) * Lc + c] += quant_error * error_factors[3];
            }
        }
    }
}

// extern "C" __declspec(dllexport)
// void floyd_steinberg(double* image, int Lx, int Ly, int Lc, float shagreen) {
//     const int sixteen = 16;
//     for (int j = 0; j < Ly; j++) {
//         for (int i = 0; i < Lx; i++) {
//             for (int c = 0; c < Lc; c++) {
//                 int idx = (j * Lx + i) * Lc + c;
//                 double old_pixel = image[idx];
//                 double rounded = std::round(old_pixel * shagreen) / shagreen;
//                 double quant_error = old_pixel - rounded;
//                 image[idx] = rounded;

//                 if (i + 1 < Lx)
//                     image[(j * Lx + (i + 1)) * Lc + c] += quant_error * 7.0 / sixteen;
//                 if (i > 0 && j + 1 < Ly)
//                     image[((j + 1) * Lx + (i - 1)) * Lc + c] += quant_error * 3.0 / sixteen;
//                 if (j + 1 < Ly)
//                     image[((j + 1) * Lx + i) * Lc + c] += quant_error * 5.0 / sixteen;
//                 if (i + 1 < Lx && j + 1 < Ly)
//                     image[((j + 1) * Lx + (i + 1)) * Lc + c] += quant_error * 1.0 / sixteen;
//             }
//         }
//     }
// }

extern "C" __declspec(dllexport)
char* get_message(char* message) {
    return message;
}