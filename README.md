# mcadvancementbot
Put your mcpath in settings.txt
Create a nightbot project, and copy the client_id and client_secert into settings.txt
Go to 
https://nightbot.tv/oauth2/authorize?client_id=YOUR_CLIENT_ID&response_type=code&scope=commands&redirect_uri=https:%2F%2F127.0.0.1
and authorize the bot to use your account
it should redirect you to a website, copy the code in the url, and paste that into settings.txt
run python app.py get_token
copy paste the access token and refresh token into settings.txt
run python app.py main
