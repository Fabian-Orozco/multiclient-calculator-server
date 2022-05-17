//Based on: https://opensource.com/article/19/4/interprocess-communication-linux-channels
#include <stdio.h>
#include <stdlib.h> 
#include <unistd.h> 
#include <string.h>

int pipeFDs[2]; // Create 2 File descriptors for the Pipe

// to compile: gcc -shared -W -o libPipe.so Pipe.c -fPIC

#define ReadEnd 0
#define WriteEnd 1

/**
 * @brief Create the a child process
 *
 * @return -1 on failure, 0 the child and one int the father
 */
int createChild()
{
    if (pipe(pipeFDs) < 0) // System call to create the Pipe
        return -1;         // Failure case

    int cpid;
    if ((cpid = fork()) >= 0) // create a child process
    {
        return cpid;
    }
    return -1; // Failure case
}

/**
 * @brief Read from the Pipe
 *
 * @return char*
 */
char *receiveMsg()
{
    char buf[1024];
    int readBytes;
    close(pipeFDs[WriteEnd]);          // child reads, doesn't write
    read(pipeFDs[ReadEnd], &buf, 1024); // child reads from the Pipe[0]
    char *str = buf;
    return str; // Return the message to Python
}

/**
 * @brief Write on the Pipe
 * 
 * @param msg message to be sent to another process
 */
void sendMsg(char *msg)
{
    char buf[1024];           // Buffer of the msg
    close(pipeFDs[ReadEnd]); // parent writes, doesn't read
    strcpy(buf, msg);
    write(pipeFDs[WriteEnd], buf, 1024); // write the bytes to the pipe
}