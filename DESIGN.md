Technical Tour

High-level Overview: Aesthetic.ly is a website built with Flask, HTML, CSS, SQL, JavaScript (within HTML files), and Python.

Quiz: Creating the quiz took up a solid chunk of time, and most of it was radio buttons (and I learned to make the text clickable as well as the actual selector). In terms of design, my biggest challenge and achievement was making Buzzfeed-style questions, where you can click images as answer choices. I did this by first visiting the Buzzfeed site to understand how they did it: it's actually a hidden radio button! I used CSS to format the button so that it's placed behind the image. I also used CSS to format an on-click highlight. For fun, I played around with other question styles, such as the slider bar, which utilized JavaScript as well, but found it ultimately less efficient than the radio inputs.

SQL Tables:
There are 4 SQL tables used in Aesthetic.ly: users, results, history, and feedback. The users table is essentially the same structure as in Finance, with a username session id and a hashed password. The results table records the results of each quiz, with each entry having a username, first, last, instagram, and aesthetic. I designed results so that the username is unique: each user can only have one recorded aesthetic at a time, and taking the quiz again would update their aesthetic in the table. If they changed their name/handle, that would get updated in the same entry as well. Complementarily, the history table records a history of all quizzes taken by all users, so it can be queried to display a history of aesthetic results for each user. The feedback table is intentionally not displayed in Aesthetic.ly, but it records a user's information and their given comments that I can review privately. These tables are constantly queried, especially results for a user's aesthetic, to display the information in Meet, History, etc.

Jinja if-else:
Aesthetic.ly's key component is being personalized to the aesthetic the user gets, so many tabs (Shop, Music, etc.) coded in HTML feature heavy utilization of if-else statements (if aesthetic is A, display this... if aesthetic is B, display that...) This was a conscious design choice to minimize the number of HTML pages I had: rather than create a separate page for each aesthetic, I'd be able to change the display of a page according to a checkable condition I could pass in from flask. Thus, the majority of functions in my app.py include a SQL query to get the user's aesthetic.

Shop: The shop's design resembles a 3-stall marketplace, with colors and items specifically chosen to match the aesthetic. Here, all items and links are hardcoded to Amazon products, which I'm currently satisfied with. I played around with the idea of using an Amazon Storefront API, but ultimately dismissed it as Amazon purposefully makes its APIs inaccessible without certain keys or IDs.

JavaScript/Sources Cited:
Aesthetic.ly is built from the foundations of my PSET 9, Finance. The core design of layout.html is derived directly from Finance, as is the formatting (e.g. display tables).
I also consulted outside sources, including StackOverflow for error checking, WW3Schools for syntax and formatting, and code from CanvasJS to make the Pie Chart. The Javascript in meet.html came directly from CanvasJS.
