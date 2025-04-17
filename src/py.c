#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <gc.h>

void* myalloc(size_t size) {
    GC_INIT();
    return GC_malloc(size);
}

char* concat(const char* str1, const char* str2) {
    if (!str1 || !str2) {
        return NULL;
    }

    size_t len1 = strlen(str1);
    size_t len2 = strlen(str2);
    size_t total_len = len1 + len2 + 1;

    char* result = (char*)myalloc(total_len);

    if (!result) {
        return NULL;
    }

    strcpy(result, str1);
    strcat(result, str2);

    return result;
}
