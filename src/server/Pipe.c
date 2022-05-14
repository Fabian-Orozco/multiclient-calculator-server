#include <sys/wait.h> // wait
#include <stdio.h>
#include <stdlib.h> // exit functions
#include <unistd.h> // read, write, pipe, _exit
#include <string.h>

// gcc -shared -W -o libPipe.so Pipe.c to compile

#define ReadEnd 0
#define WriteEnd 1

/**
 * @brief Send a msg to new process.
 *
 * This method create a Pipe and send message to a new child process
 *
 * @param msg
 * @return char*
 */
char *sendMsg(char *msg)
{
    int pipeFDs[2];            // Create 2 File descriptors for the Pipe
    pipe(pipeFDs);             // System call to create the Pipe
    char buf[512];            // Buffer to riceibe the msg
    int readBytes;

    pid_t cpid = fork(); // fork a child process
    if (cpid < 0)
        exit(0); // check for failure

    if (0 == cpid) // child process work
    {
        close(pipeFDs[WriteEnd]); // child reads, doesn't write
        
        read(pipeFDs[ReadEnd], &buf, 512);// child reads from the Pipe[0]
        close(pipeFDs[ReadEnd]); // close the Pipe
        char *str = buf;
        return str; // Return the message to Python
    }

    else // father process work
    {
        close(pipeFDs[ReadEnd]); // parent writes, doesn't read
        strcpy(buf, msg);
        write(pipeFDs[WriteEnd], buf, 512); // write the bytes to the pipe
        close(pipeFDs[WriteEnd]);                   // done writing: generate eof
        char *str = "papa";
        return str;
    }
}
