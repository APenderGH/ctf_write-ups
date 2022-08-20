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

```c
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

Okay, it's about to get a bit technical. This output shows that values on the stack are being overwritten by our input. If you're not familiar with the stack at all there's plenty of resources explain how the stack works, for now I'll just be explaining how we can abuse this overflow.

Now, this explain why we get our segfault, we're overwriting the value in the EIP register. The EIP register is supposed to point to the next instruction we want to execute, instead its pointing to `0x41414141` (`0x41` == 'A'). But this is good, this means we can control where our program goes if we put a valid address in EIP.

We wanna get to the `system()` call inside the `win()` function, so lets find the address for that instruction. We can do this in `gdb` by disassembling the `win()` function, showing all the addresses and offsets for the assembly instructions.

```
pwndbg> disassemble win
Dump of assembler code for function win:
   0x08049196 <+0>:     push   ebp
   0x08049197 <+1>:     mov    ebp,esp
   0x08049199 <+3>:     push   ebx
   0x0804919a <+4>:     sub    esp,0x4
   0x0804919d <+7>:     call   0x80490d0 <__x86.get_pc_thunk.bx>
   0x080491a2 <+12>:    add    ebx,0x2e52
   0x080491a8 <+18>:    cmp    DWORD PTR [ebp+0x8],0xdeadbeef
   0x080491af <+25>:    jne    0x80491e8 <win+82>
   0x080491b1 <+27>:    cmp    DWORD PTR [ebp+0xc],0x1337c0de
   0x080491b8 <+34>:    jne    0x80491e8 <win+82>
   0x080491ba <+36>:    sub    esp,0xc
   0x080491bd <+39>:    lea    eax,[ebx-0x1fec]
   0x080491c3 <+45>:    push   eax
   0x080491c4 <+46>:    call   0x8049040 <puts@plt>
   0x080491c9 <+51>:    add    esp,0x10
   0x080491cc <+54>:    sub    esp,0xc
   0x080491cf <+57>:    lea    eax,[ebx-0x1faf]
   0x080491d5 <+63>:    push   eax
   0x080491d6 <+64>:    call   0x8049050 <system@plt>    <---- Here's that system call
   0x080491db <+69>:    add    esp,0x10
   0x080491de <+72>:    sub    esp,0xc
   0x080491e1 <+75>:    push   0x0
   0x080491e3 <+77>:    call   0x8049060 <exit@plt>
   0x080491e8 <+82>:    nop
   0x080491e9 <+83>:    mov    ebx,DWORD PTR [ebp-0x4]
   0x080491ec <+86>:    leave
   0x080491ed <+87>:    ret
End of assembler dump.
pwndbg>
```
So we know the address of the `system()` call (`0x080491d6`). So if we can control EIP, why don't we just jump straight there? Well when a function gets called in assembly it first has to push its parameters onto the stack. We can see this behaviour here.

```c
void win(int a, int b) {
    if (a == 0xdeadbeef && b == 0x1337c0de) {
        printf("Congratz! Cat the flag and sent it to @deluqs in the Discord\n");
        system("/bin/sh");
        exit(0);  //<--- This is the function we're looking at, it takes a parameter of 0 in the source code.
    }
    return;
}
```
Now lets look at the assembly,
```
0x080491e1 <+75>:    push   0x0   <--- This pushes the parameter, 0, onto the stack
0x080491e3 <+77>:    call   0x8049060 <exit@plt>  <--- This calls the exit function, it grabs its parameters off of the stack
```
So, if we're looking at the `system()` call,
```c
void win(int a, int b) {
    if (a == 0xdeadbeef && b == 0x1337c0de) {
        printf("Congratz! Cat the flag and sent it to @deluqs in the Discord\n");
        system("/bin/sh"); //<--- This is the function we're looking at, it takes a parameter of "/bin/sh"
        exit(0);
    }
    return;
}
```
The assembly...
```
0x080491d5 <+63>:    push   eax  <--- Pushes its parameter onto the stack (in this case its parameter is stored in EAX)
0x080491d6 <+64>:    call   0x8049050 <system@plt> <--- Calls the system function, grabs its parameter off the stack
```
So this means we cant just jump straight to `0x080491d6` because the `system()` function won't have a parameter to use. One way we can solve this is by also overwriting EAX with a pointer to the string "/bin/sh", then, instead of jumping to `0x080491d6` we jump to `0x080491d5` so that our value in EAX gets pushed to the stack before `system()` is called. 

Okay, so know our input needs to do the following:
- Overflow the buffer until we reach the EAX register
- Overwrite the EAX register with a pointer to "/bin/sh"
- Continue to overflow the buffer until we reach EIP
- Overwrite EIP with the address to the assembly instruction just before the `system()` call



