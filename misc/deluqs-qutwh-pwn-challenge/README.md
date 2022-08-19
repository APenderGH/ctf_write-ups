<p align="center">
  <img width="500" src="delqut.png" alt="Intro to Binary Exploitation">
</p>
<h1 align="center" style="margin-top: 0px;">Deluqs - Intro to Binary Exploitation for the QUTWH</h1>

<p>
Deluqs gave an awesome talk at QUT introducing us to binary exploitation. At the end of his presentation he gave the QUT whitehats a challenge to do, the first person to get the flag would get a ticket to Crikeycon! Let's take a look at what we've got.
  
Alright, so we're given a repository. Cloning it, we get these files:
</p>

![image](https://user-images.githubusercontent.com/104875856/185619589-a41a3f81-d303-4b48-b005-aaebb60e5eb3.png)

Pretty quickly we should realise that these files look like a docker container, so we've likely got to connect to a remote server at some point to get the flag. We're given the server details in `README.md`.

Anyway, the files we should be focused on are `challenge` and `challenge.c`. `Challenge` is the binary we want to exploit, `challenge.c` is it's C source code. 
Running `file` on `challenge` we see we've got an unstripped binary with debug info.

![image](https://user-images.githubusercontent.com/104875856/185620992-41056b2e-04ef-4f2e-b63a-884358cfa794.png)

Quickly running the binary shows us its base functionality.

![image](https://user-images.githubusercontent.com/104875856/185621404-0304bf3c-e1dc-4ed6-8da7-b4ff7ed55062.png)

Cool, so the binary takes input and tells us if we've exploited it? Let's take a look at the source code.

```cs
#include <stdio.h>
#include <stdlib.h>

void win(int a, int b) {
    if (a == 0xdeadbeef && b == 0x1337c0de) {
        printf("Congratz! Cat the flag and sent it to @deluqs in the Discord\n");
        system("/bin/sh"); //We want to run this, but win() is never called
        exit(0);
    }
    return;
}

int vuln() {
    int b;
    char buffer[40]; //Buffer size of 40 characters (it can only fit 40 characters of our input)
    b = 0;
    printf("Can you exploit this?\n");
    gets(&buffer); //Oh, what's this?! https://linux.die.net/man/3/gets
    return b;
}

void main() {
    vuln();
    printf("You did not exploit it.\n");
    return;
}
```

So our objective is clear, we want to execute the win() function and get to that system() call. When looking for vulnerabilities, a good place to start is looking at what you control. In this case, we control what gets put into that char buffer, so lets look into how that happens.

Well, it's pretty simple actually, this function `gets()` takes our input and puts it into our buffer. But taking a closer look at the documentation for the `gets()` function,
>gets() reads a line from stdin into the buffer pointed to by s until either a terminating newline or EOF, which it replaces with a null byte (aq\0aq). No check for buffer overrun is performed (see BUGS below). 
Okayyyy, that's weird. So this `gets()` function takes input from stdin until it hits a newline and then just throws it all in our buffer. But we saw earlier in our source code that the size of our buffer is only 40 characters. Yeah, `gets()` doesn't care about this, we could put in 100 characters and its still gonna try squeeze it in there.

So what happens when we do that?

![image](https://user-images.githubusercontent.com/104875856/185718518-a9e5d94e-ecfd-4645-ade3-aa4ad95eb3dc.png)

Ooooo, a seg fault. A staple indication of a buffer overflow (when your buffer gets overflown!!!). Okay, so this pesky `gets()` function overflows our buffer, where does the rest of our input go then? And why do we get a seg fault?

A useful tool for looking into this sort of stuff is a debugger, `gdb` is my debugger of choice especially for ELF binaries. So, running the binary with `gdb` attached and using the same input we did before, we get this.

![image](https://user-images.githubusercontent.com/104875856/185719252-4af49605-8c4a-4f13-8855-8ecb98c5a8ac.png)
