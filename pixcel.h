#include <stdio.h>
#include <math.h>
#include <time.h>

void _pwp(unsigned char* image, unsigned char* mask, int* f, int height, int width, int bits)
{
    int i = 0, j = 0;
    //int f [32][32][32] = {0};

    //clock_t begin = clock();
    //clock_t end = 0;
    //double time_spent = 0;
    
    for(i = 0, j = 0; i < height * width * 3; i += 3, j++)
    {
        if(mask[j] == 1)
        {
            f[image[i]/8 * 1024 + image[i + 1]/8 * 32 + image[i + 2]/8]++;
        }
        else
        {
            f[image[i]/8 * 1024 + image[i + 1]/8 * 32 + image[i + 2]/8]--;
        }
    }
    
    for(i = 0, j = 0; i < height * width * 3; i += 3, j++)
    {
        if(f[image[i]/8 * 1024 + image[i + 1]/8 * 32 + image[i + 2]/8] > 0)
        {
            mask[j] = 255;
        }
        else
        {
            mask[j] = 0;
        }
    }

    //end = clock();
    //time_spent = (double)(end - begin) / CLOCKS_PER_SEC;
    //printf("Execution time %lf", time_spent);
}


void _applyModel(unsigned char* image, unsigned char* mask, int* f, int height, int width)
{
    int i = 0, j = 0;
    for(i = 0, j = 0; i < height * width * 3; i += 3, j++)
    {
        if(f[image[i]/8 * 1024 + image[i + 1]/8 * 32 + image[i + 2]/8] > 0)
        {
            mask[j] = 255;
        }
        else
        {
            mask[j] = 0;
        }
    }
}

void _computePosteriors(unsigned char* image, unsigned char* mask, int* f, int height, int width)
{
    int i = 0, j = 0;
    for(i = 0, j = 0; i < height * width * 3; i += 3, j++)
    {
        if(mask[j] == 1)
        {
            f[image[i]/8 * 1024 + image[i + 1]/8 * 32 + image[i + 2]/8]++;
        }
        else
        {
            f[image[i]/8 * 1024 + image[i + 1]/8 * 32 + image[i + 2]/8]--;
        }
    }
    
}
