<p align="center">
  <img width="600" src="Challenge.PNG" alt="Challenge Description">
</p>
<h1 align="center" style="margin-top: 0px;">Uni of Straya - Part 1</h1>

Daaamn, that description is long, looks pretty scary. Luckily for this first part we just need to focus on that first point.

**Bypass authorization and view the admin console located at ``/admin``**

Alright, so here's what the main page looks like.

![image](https://user-images.githubusercontent.com/104875856/192207126-5cfea71c-55c4-4759-921e-14ebd3321df5.png)

Registering and logging in we get a similar looking page with different prompts. All of which don't give any useful information. 

![image](https://user-images.githubusercontent.com/104875856/192207247-d59e95db-851d-44fd-8f84-e6ae48680ced.png)

Trying to go to `/admin` we get logged out and redirected to the main screen.

I wanted to see what kind of authentication was being used and looking in our web storage we've got a JWT token stored in local storage, there's also a field for userId but changing this does nothing.

At this point I wanted to look into what javascript was being run on each page, since I noticed a `main.js` and `dashboard.js` in the source of the two pages we've been to so far. Every `.js` and `.html` file I came across I saved locally and opened up in Visual Studio Code, that way I can easily navigate and see what's going on.

Once I had all that set out I wanted to take a deeper look into what happens when we request `/admin` since I noticed when we try load the page sometimes the webpage loads for a second and then we get redirected.

Loading up burpsuite and requesting the page serves us html, if we render that it looks like this.

![image](https://user-images.githubusercontent.com/104875856/192208545-30bd1a2d-a8c3-406a-b639-bd0c1c6a6193.png)

That page refers to an `admin.js` file, so I saved the source for that file too.

Now that I had the important `.html` and `.js` files I spent a long time analysing them. A quick realisation was that there were heaps of calls to an API. I tested this API a lot using https://reqbin.com/, definitely my favourite tool for this kind of stuff. I quickly realised that our authorisation was very limited, the JWT token of a standard user only allows us to access a few functionalities. On the topic of our JWT token, here's what it looks like decoded using https://jwt.io/ (another great tool).

![image](https://user-images.githubusercontent.com/104875856/192209919-67b90291-57fd-4648-aef6-a804f22150cc.png)

Notice anything interesting? For me, that directory looked super interesting. As soon as I saw that I thought I might be able to get SSRF (Server-Side Request Forgery). SSRF is where you get the server itself to make a request to wherever you want. My idea was that maybe the server has to follow that directory when it goes to sign our JWT for authentication, if we can change that then maybe we can get it to send a request to somewhere other than `/api/auth/pub-key`.

To test this I crafted a new JWT, keeping everything else the same but changing the header to this:

```json
{
  "alg": "RS256",
  "iss": "https://requestbin.io/z39ug0z3",
  "typ": "JWT"
}
```
https://requestbin.io is a great website for grabbing http callbacks, you can just generate and link and it will log any request made to it.

Sending a request to an API endpoint we don't have access to gives us this response:

```json
{
    "result": "M8 you broke something: ISS needs to match ^/api/auth/pub-key!",
    "status": "error"
}
```

Hm, okay, that regex seems pretty easy to bypass. We could use something like ``/api/auth/pub-key/../../../../`` to get back to the base url. The only problem now is that we can't pass in a straight url since it will try to use it as a directory, it's not just slapped into a request, in fact I made this mistake in my last payload as well, that would've never worked because the original payload had a relative path.

As soon as I ran into this issue I went back to the source code I had, almost immediately I noticed this in `admin.js`!!!

```js
setInterval(() => {
        authAjax({
            url: "/api/auth/isstaff",
            type: "GET",
            success: (data) => {
                if (data.status === "error") {
                    window.location = "/api/auth/logout?redirect=/logout";
                }
            },
            error: errorCallback
        });
    }, 60000);
```

Do you see that? There's an api endpoint that redirects the user to a url. That's how it was kicking us out of the page, that also explains why sometimes it wouldn't kick us out immediately, it had to wait for the api.

Anyway, this is huge! If we can make the server go to this endpoint we can control where it gets redirected, aka **SSRF**!!!. Let's make the payload!

Alright so we know we can get to the base url using directory traversal ``/api/auth/pub-key/../../../../``, now we just need to go to the logout endpoint. That looks like this,

``/api/auth/pub-key/../../../../api/auth/logout?redirect=EVIL``

Let's put our requestbin url in our EVIL parameter and throw it in a JWT. Our JWT header now looks like this.

```json
{
  "alg": "RS256",
  "iss": "/api/auth/pub-key/../../../../api/auth/logout?redirect=https://requestbin.io/z39ug0z3",
  "typ": "JWT"
}
```

Sending that through...

```json
{
    "result": "M8 you broke something: ('Could not deserialize key data. The data may be in an incorrect format, it may be encrypted with an unsupported algorithm, or it may be an unsupported key type (e.g. EC curves with explicit parameters).', [_OpenSSLErrorWithText(code=75497580, lib=9, reason=108, reason_text=b'error:0480006C:PEM routines::no start line')])",
    "status": "error"
}
```

NO WAY

![image](https://user-images.githubusercontent.com/104875856/192215883-ad5f5900-69e7-4b26-be1a-5fef57785e68.png)

So we have SSRF, but it's kinda limited right? We don't get any real feedback on what the server other than that error message. I tried for a while to get that error message to maybe leak some of the content that it retrieved, if we could do that then we might be able to view a response from the api that we aren't authorised to see.

When I determined that wouldn't work I started thinking, if we control where the server goes for a public key then we can route it to our own public key! Now, I don't completely understand how key pair verification works with JWT's RS256 algo, but I'll explain how I think it works from what research I've done.

*at this point it's also important to note that the 'alg' specified in the JWT header was RS256, this involves RSA key pairs*

- First, you need an RSA key pair. First you generate a private key, and from that private key you generate a public key.
- Then, we sign the JWT token with our Private key.
- When we want to verify a JWT token, we check it against our public key. Since **anything signed by our private key can only be verified by the corresponding public key**.

This means on the api end, they've created the JWT with their private key and then they look for the public key to verify it against. The issue with this is that **they only check if the private key used to make the JWT corresponds with the public key they find using that directory**.

This means we can make our own JWT, signed with **our own private key** and then point the verification to **our own public key**. The JWT will be valid because it was created and verified against a valid key pair.

Pheew, alright. Now that we've got that, how can we set it up? Well, first we generate an RSA key pair (you can do this using ssh-keygen).

![image](https://user-images.githubusercontent.com/104875856/192242616-1f492dd5-1028-43ea-ab71-ab7d1690df2c.png)

Awesome, now we need make our JWT using the private key. We can do this super easily with https://jwt.io/, and if we plug in our public key as well it'll tell us if the signature is correct.

![image](https://user-images.githubusercontent.com/104875856/192243558-982836a2-2348-4613-837b-d55ddc9cd48a.png)

Great! So it's telling us that the JWT is valid and it'll be authenticated using that key pair. Now, when we send this to the api we don't want to be our current user, we wanna become someone with privileges, so I'm gonna change that `userId` to 1 and hope that the first user has permissions.

![image](https://user-images.githubusercontent.com/104875856/192243976-731e21fb-957f-4046-ae87-f575ddabe23d.png)

There's still one issue though, we need to make sure that the server uses OUR public key to authenticate the JWT token. So first we need to expose our public key file to the internet. I'll do this using a python http server and ngrok.

First, make a python server listen on port 8000.

![image](https://user-images.githubusercontent.com/104875856/192244462-8c689fca-dee3-4994-b7a0-0cf0ce0227b9.png)

Second, start a front facing (front facing means its accessible on the open web) ngrok server pointing to our HTTP python server.

![image](https://user-images.githubusercontent.com/104875856/192244694-46746173-654e-4ae2-9efb-1fcea9070e77.png)

![image](https://user-images.githubusercontent.com/104875856/192244765-e2ade595-d107-4331-9065-6dccc0e4fc00.png)

Awesome, now the url http://0.tcp.au.ngrok.io:19528/jwtRS256.key.pub will serve our public key.

Change our JWT token to point to this address for public key authentication, which looks like this:

![image](https://user-images.githubusercontent.com/104875856/192245367-994d57ce-352b-49c0-83df-575c1acea8ed.png)

Now, let's use this JWT token and try to access `/admin`.

![image](https://user-images.githubusercontent.com/104875856/192245728-a10fbc6f-cf26-4ec0-a14f-bcab9ceaddbf.png)

WOOOOOOOOOOOOOOOOOOOOOOOOOO!! IT WORKED!! HAHAA <- my actual reaction when this worked

We got our flag!!
`DUCTF{iSs_t0_h0vSt0n_c4n_U_h3r3_uS_oR_r_w3_b31nG_r3dIrEcTeD!1!}`

This was such an awesome challenge, I really think this has been one of the most satisfying flags I've ever gotten. I really gotta give it to `ghostccamm`, the author of this challenge, the vector going from directory traversal to SSRF and finally to a forged JWT token was so awesome and it taught me heaps! This flag alone made DUCTF awesome for me and I can't wait for the next one.

Thanks for reading all of this, I hope it was useful to you in some way!
