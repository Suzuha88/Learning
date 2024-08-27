#include <cs50.h>
#include <ctype.h>
#include <stdbool.h>
#include <stdio.h>
#include <string.h>

string substitute(string input, string key);
bool keyIsValid(string key);

int main(int argc, string argv[])
{
    string key = argv[1];

    if (argc == 2 && keyIsValid(key)) // if user input is correct procced with the programm
    {
        string plainText = get_string("plaintext: ");
        printf("ciphertext: %s\n", substitute(plainText, key));
    }
    else if (argc != 2) // check if number of arguments is the problem
    {
        printf("Usage: ./substitution key\n");
        return 1;
    }
    else // if problem isn't with the number of arguments, then key is wrong
    {
        printf("Key must contain 26 unique english characters\n");
        return 1;
    }
}

string substitute(string input, string key)
{
    string output = input; // this is to make sure what output and input have same length

    for (int i = 0; input[i] != 0; i++)
    {
        if (input[i] >= 'a' && input[i] <= 'z') // checking to keep case same in output as in input
        {
            output[i] = tolower(key[input[i] - 'a']);
        }
        else if (input[i] >= 'A' && input[i] <= 'Z')
        {
            output[i] = toupper(key[input[i] - 'A']);
        }
    }
    return output;
}

bool keyIsValid(string key)
{
    int length = strlen(key);
    if (length != 26)
    {
        return false;
    }
    else
    {
        bool charWasInKey[26] = {
            false}; // array of bool values, checking if value was seen in key already
        for (int i = 0; key[i] != 0; i++)
        {
            if (!((key[i] >= 'a' && key[i] <= 'z') ||
                  (key[i] >= 'A' && key[i] <= 'Z'))) // check if character isn'y alphabetical
            {
                return false;
            }
            if (charWasInKey[tolower(key[i]) - 'a']) // check if character is was seen in key
            {
                return false;
            }
            else
            {
                charWasInKey[tolower(key[i]) - 'a'] = true; // toggle "char was seen already" value
            }
        }
        return true;
    }
}
