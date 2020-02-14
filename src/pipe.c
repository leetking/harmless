#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "pipe.h"

static int read_end = 0;
static int eof = 0;

# include <signal.h>
# include <time.h>
# include <sys/select.h>
# include <unistd.h>

void open_pipe()
{
    eof = 0;
    read_end = 0;
}


void close_pipe()
{
}


void line_output(const char *line_str)
{
    printf("%s\n", line_str);
}

static int read_line(char *buff, int n)
{
    int ch;
    int i;
    for (i = 0; i < n-1; i++) {
        ch = getchar();
        if ('\n' == ch || EOF == ch)
            break;
        buff[i] = ch;
    }
    buff[i] = '\0';

    return i;
}


int line_input(char *line_str)
{
    return read_line(line_str, LINE_INPUT_MAX_CHAR);
}
