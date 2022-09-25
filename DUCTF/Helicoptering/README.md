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
**one/.htaccess**

RewriteEngine On
RewriteCond %{HTTP_HOST} !^localhost$
RewriteRule ".*" "-" [F]
```
