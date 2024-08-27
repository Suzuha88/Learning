// Implements a dictionary's functionality
#define _GNU_SOURCE
#include <ctype.h>
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "dictionary.h"

// Represents a node in a hash table
typedef struct node
{
    char word[LENGTH + 1];
    struct node *next;
} node;

bool clear(node *cell);
bool find(const char *str, node *cell);

// TODO: Choose number of buckets in hash table
const unsigned int N = 1000;
int wordCount = 0;

// Hash table
node *table[N];

// Returns true if word is in dictionary, else false
bool check(const char *word)
{
    return find(word, table[hash(word)]);
}

// Hashes word to a number
unsigned int hash(const char *word)
{
    unsigned int hashCode = 0;
    for (int i = 0, l = strlen(word); i < l; i++)
    {
        if (isalpha(word[i]))
        {
            hashCode += (toupper(word[i]) - 'A') + (i * 26);
        }
    }

    return hashCode % N;
}

// Loads dictionary into memory, returning true if successful, else false
bool load(const char *dictionary)
{
    FILE *dict = fopen(dictionary, "r");
    if (dict == NULL)
    {
        return false;
    }

    char *str = NULL;
    size_t len = 0; // dummy value to put into getline
    while (getline(&str, &len, dict) != -1)
    {
        node *cell = malloc(sizeof(node));
        for (int i = 0, l = strlen(str); i < l; i++)
        {
            if (str[i] == '\n')
            {
                cell->word[i] = 0;
            }
            else
            {
                cell->word[i] = str[i];
            }
        }
        cell->next = NULL;

        unsigned int hashCode = hash(str);
        if (table[hashCode])
        {

            node *tmp = table[hashCode];

            table[hashCode] = cell;
            table[hashCode]->next = tmp;
            wordCount++;
        }
        else
        {
            table[hashCode] = cell;
            wordCount++;
        }
    }
    free(str);
    fclose(dict);
    return true;
}

// Returns number of words in dictionary if loaded, else 0 if not yet loaded
unsigned int size(void)
{
    return wordCount;
}

// Unloads dictionary from memory, returning true if successful, else false
bool unload(void)
{
    for (int i = 0; i < N; i++)
    {
        if (!clear(table[i]))
        {
            return false;
        }
    }
    return true;
}

bool clear(node *cell)
{
    if (!cell) // if cell was empty from the beginning
    {
        return true;
    }
    else if (cell->next) // if not the last cell in the list
    {
        clear(cell->next);
        cell->next = NULL;
    }
    if (!cell->next) // if the last cell in the list
    {
        free(cell);
        return true;
    }
    else // if couldn't clear a cell
    {

        return false;
    }
}

bool find(const char *str, node *cell)
{
    if (cell)
    {
        if (strcasecmp(cell->word, str) != 0)
        {

            return find(str, cell->next);
        }
        else
        {
            return true;
        }
    }
    else
    {

        return false;
    }
}
