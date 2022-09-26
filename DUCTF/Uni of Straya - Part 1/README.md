<p align="center">
  <img width="600" src="Challenge.PNG" alt="Challenge Description">
</p>
<h1 align="center" style="margin-top: 0px;">Uni of Straya - Part 1</h1>

Daaamn, that description is long, looks pretty scary. Luckily for this first part we just need to focus on that first point.

**Bypass authorization and view the admin console located at ``/admin``**

Alright, so here's what the main page looks like.

![image](https://user-images.githubusercontent.com/104875856/192207126-5cfea71c-55c4-4759-921e-14ebd3321df5.png)

Registering and logging in we get a similar looking page with different prompts. All of which don't give any useful information. Trying to go to `/admin` we get redirected to the main screen.

![image](https://user-images.githubusercontent.com/104875856/192207247-d59e95db-851d-44fd-8f84-e6ae48680ced.png)

I wanted to see what kind of authentication was being used and looking in our web storage we've got a JWT token stored in local storage, there's also a field for userId but changing this does nothing.

At this point I wanted to look into what javascript was being run on each page, since I noticed a `main.js` and `dashboard.js` in the source of the two pages we've been to so far. Every `.js` and `.html` file I came across I saved locally and opened up in Visual Studio Code, that way I can easily navigate and see what's going on.

Once I had all that set out I wanted to take a deeper look into what happens when we request `/admin` since I noticed when we try load the page sometimes the webpage loads for a second and then we get redirected.


