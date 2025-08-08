Method 2: Using the Heroku Dashboard Console
If you prefer not to install the Heroku CLI, you can run the script directly from the Heroku website.

Log in to your Heroku account and go to your dashboard: https://dashboard.heroku.com

Select your bot's application from the list.

In the top-right corner of the page, click on the "More" button.

From the dropdown menu, select "Run console".

A new page will open. In the input field, type the following command:

Bash

```python3 create_index.py```
Click the "Run" button next to the input field.

Heroku will then execute the script. You will see the output in the console window below, and it will show a message like "Text index created successfully!" when it is finished.

```
start - check bot alive
settings - get settings 
logs - to get the rescent errors
restart - restart the server
update - update from git latest 
stats - to get status of files in db.
filter - add manual filters
filters - view filters
connect - connect to PM.
disconnect - disconnect from PM
connections - check all connections
del - delete a filter
delall - delete all filters
deleteall - delete all index(autofilter)
delete - delete a specific file from index.
info - get user info
id - get tg ids.
imdb - fetch info from imdb.
users - to get list of my users and ids.
chats - to get list of the my chats and ids 
leave  - to leave from a chat.
disable  -  do disable a chat.
enable - re-enable chat.
ban_user  - to ban a user.
unban_user  - to unban a user.
channel - to get list of total connected channels
broadcast - to broadcast a message to all Eva Maria users
```

