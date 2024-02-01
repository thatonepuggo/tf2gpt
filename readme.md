# epic rcon ai thing!!
lets people in source games run ";ask" to ask an ai a question.

# how to run
you need the python packages rcon, replicate, and python-dotenv but i forgot to add a requirements.txt

first off, add these lines to your `tf/cfg/autoexec.cfg`:
```cfg
ip 0.0.0.0
rcon_password dontcarelol // edit this if you want
net_start
```
you dont have to edit the rcon_password since the port for rcon likely isnt open, but if you do, edit `main.py` and change the PASSWORD variable to reflect that change.

if you do not already have a replicate account, you can make one by going to this link: https://replicate.com

change the .env_example file to include your discord bot token and your replicate api token.
rename .env_example to .env

in main.py, you can edit the prompt to your liking or you can leave it the same as it is.

# thanks to
nickplj12 (for mercenary discord bot, which this is sorta based off of)

Meta (for llama)

AlphaBlaster

dotheboogey678
