<p align="center">
  <img width="600" src="Challenge.PNG" alt="Challenge Description">
</p>
<h1 align="center" style="margin-top: 0px;">Helicoptering</h1>

Alright, so going to the link they give us we get this webpage.

![image](https://user-images.githubusercontent.com/104875856/192170071-8f6d9507-d92c-4f4e-980a-c570191e9dc5.png)

Okay, so first thing I notice is all these helicopter references. Apache is a common web server software but it's also a type of attack helicopter. Sooooo, which one could it be? Here, take your pick:

War-machine             |  HTTP server
:-------------------------:|:-------------------------:
| ![image](https://user-images.githubusercontent.com/104875856/192170186-4bce1d3b-7500-4260-8e30-06793216624a.png) |  ![image](https://user-images.githubusercontent.com/104875856/192170208-6c87c791-29cb-4f0e-9306-506cd57c4b10.png) |

As much as I'd love to imagine our server is being run on an Apache attack helicopter, it seems more likely that this server is running the Apache HTTP service. 

Now, the webpage tells us we need to access two directories

(1) http://34.87.217.252:30026/one/flag.txt
(2) http://34.87.217.252:30026/two/flag.txt

The webpage also gives us the content of the .htaccess files for both directories. If you're not familiar, a quick google search for .htaccess files will tell you its contents is used in apache to create custom configurations for specific directories.

So lets start with the first one

```
one/.htaccess

RewriteEngine On
RewriteCond %{HTTP_HOST} !^localhost$
RewriteRule ".*" "-" [F]
```

Without knowing any of this syntax there's a few things I recognise. We've got a 'RewriteCond' which I assume is the condition it checks when we try to go to the directory, and inside that condition I see a bit of regex. That regex is `^localhost$`, the `^` denotes the beginning of a string and `$` denotes the end. That means the regex will only match strings that are exactly `localhost`. Alright, but what's that `%{HTTP_HOST}` thingo? Well I just pasted that into google and found this stack exchange page:

![image](https://user-images.githubusercontent.com/104875856/192171027-90c263b8-0050-46e8-beeb-59b20f051ceb.png)

If that looks like a lot of random words, don't worry. We only need to focus on that very first sentence.

`The HTTP_HOST server variable contains the value of the Host HTTP request header`.

So when we send a request to a website our request looks something like this,

![image](https://user-images.githubusercontent.com/104875856/192171109-d738db53-a5da-4b90-8be7-c26d37b8051d.png)

Notice those blue highlighted fields, they're the **request headers** that you sent to the server. Different headers are used in different contexts, you'll see the common ones a lot and some other ones less frequently, but there's plenty of documentation for them and you'll pick up the common ones pretty quick.

Anyway, we know from that stack exchange post that `%{HTTP_HOST}` holds the value of the `Host` header. We can actually see what that value was in my example above, in there the `Host` header was set to `34.87.217.252:30026`. So now the solution seems pretty obvious, we need to get our `Host` header to be `localhost` when we request `/one/flag.txt`.

We can do this inside of burpsuite pretty easily, intercepting a request to `/one/flag.txt`, changing the `Host` header to equal `localhost` and sending it through.
Making that change, our request then looks like this,

![image](https://user-images.githubusercontent.com/104875856/192171420-de744843-8073-45d3-aa45-06e9b4a0a6d9.png)

Sending it through and we get the first flag

![image](https://user-images.githubusercontent.com/104875856/192171456-66b2ed1c-65c8-4356-a8c3-0edbda0d16a2.png)




