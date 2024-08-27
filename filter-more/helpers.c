#include <math.h>
#include <stdio.h>

#include "helpers.h"

float pythagor(int x, int y);

// Convert image to grayscale
void grayscale(int height, int width, RGBTRIPLE image[height][width])
{
    for (int i = 0; i < height; i++)
    {
        for (int j = 0; j < width; j++)
        {
            int average = floor(
                (image[i][j].rgbtBlue + image[i][j].rgbtGreen + image[i][j].rgbtRed) / 3.0 + 0.5);
            image[i][j].rgbtBlue = average;
            image[i][j].rgbtGreen = average;
            image[i][j].rgbtRed = average;
        }
    }
    return;
}

// Reflect image horizontally
void reflect(int height, int width, RGBTRIPLE image[height][width])
{
    RGBTRIPLE imageCopy[height][width];
    for (int i = 0; i < height; i++)
    {
        for (int j = 0; j < width; j++)
        {
            imageCopy[i][j] = image[i][j];
        }
    }
    for (int i = 0; i < height; i++)
    {
        for (int j = 0; j < width; j++)
        {
            image[i][j] = imageCopy[i][width - j - 1];
        }
    }
    return;
}

// Blur image
void blur(int height, int width, RGBTRIPLE image[height][width])
{
    RGBTRIPLE imageCopy[height][width];
    for (int i = 0; i < height; i++)
    {
        for (int j = 0; j < width; j++)
        {
            imageCopy[i][j] = image[i][j];
        }
    }
    for (int i = 0; i < height; i++)
    {
        for (int j = 0; j < width; j++)
        {
            uint16_t sumBlue = 0;
            uint16_t sumGreen = 0;
            uint16_t sumRed = 0;
            int count = 0;
            for (int y = i - 1; y < i + 2; y++)
            {
                for (int x = j - 1; x < j + 2; x++)
                {
                    if (x >= 0 && y >= 0 && x < width && y < height)
                    {
                        sumBlue += imageCopy[y][x].rgbtBlue;
                        sumGreen += imageCopy[y][x].rgbtGreen;
                        sumRed += imageCopy[y][x].rgbtRed;
                        count++;
                    }
                }
            }

            image[i][j].rgbtBlue = floor((float) sumBlue / count + 0.5);
            image[i][j].rgbtGreen = floor((float) sumGreen / count + 0.5);
            image[i][j].rgbtRed = floor((float) sumRed / count + 0.5);
        }
    }
    return;
}

// Detect edges
void edges(int height, int width, RGBTRIPLE image[height][width])
{
    RGBTRIPLE imageCopy[height][width];
    for (int i = 0; i < height; i++)
    {
        for (int j = 0; j < width; j++)
        {
            imageCopy[i][j] = image[i][j];
        }
    }
    const int Gx[3][3] = {{-1, 0, 1}, {-2, 0, 2}, {-1, 0, 1}};
    const int Gy[3][3] = {{-1, -2, -1}, {0, 0, 0}, {1, 2, 1}};

    for (int i = 0; i < height; i++)
    {
        for (int j = 0; j < width; j++)
        {
            // can't create rgbtripple because need bigger int
            int sumBlueX = 0;
            int sumGreenX = 0;
            int sumRedX = 0;

            int sumBlueY = 0;
            int sumGreenY = 0;
            int sumRedY = 0;
            for (int y = i - 1; y < i + 2; y++)
            {
                for (int x = j - 1; x < j + 2; x++)
                {
                    if (x >= 0 && y >= 0 && x < width && y < height)
                    {
                        sumBlueX += Gx[y - i + 1][x - j + 1] * imageCopy[y][x].rgbtBlue;
                        sumGreenX += Gx[y - i + 1][x - j + 1] * imageCopy[y][x].rgbtGreen;
                        sumRedX += Gx[y - i + 1][x - j + 1] * imageCopy[y][x].rgbtRed;

                        sumBlueY += Gy[y - i + 1][x - j + 1] * imageCopy[y][x].rgbtBlue;
                        sumGreenY += Gy[y - i + 1][x - j + 1] * imageCopy[y][x].rgbtGreen;
                        sumRedY += Gy[y - i + 1][x - j + 1] * imageCopy[y][x].rgbtRed;
                    }
                }
            }

            image[i][j].rgbtBlue = floor(fmin(pythagor(sumBlueX, sumBlueY), 255) + 0.5);
            image[i][j].rgbtGreen = floor(fmin(pythagor(sumGreenX, sumGreenY), 255) + 0.5);
            image[i][j].rgbtRed = floor(fmin(pythagor(sumRedX, sumRedY), 255) + 0.5);
        }
    }
    return;
}

float pythagor(int x, int y)
{
    return sqrt(x * x + y * y);
}
