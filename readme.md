# epic rcon ai thing!!
lets people in source games run ";ask" to ask an ai a question.

# how to run

## dependencies

install the dependencies: `pip install -r requirements.txt`

install vlc [here](https://www.videolan.org/)

get [virtual audio cable](https://vb-audio.com/Cable/). this will let you use tts response message with the ;ask command.

## launch options and autoexec

add the following to your launch options:
```
-condebug -conclearlog -usercon -g15
```

then, add these lines to your `cfg/autoexec.cfg`:
```js
ip 0.0.0.0
rcon_password dontcarelol // edit this if you want
net_start
```

run `python setup.py` and go through the prompts

you dont have to edit the rcon_password since the port for rcon likely isnt open, but if you do, edit `config.yaml` and change the `password` variable to reflect that change.

in `config.yaml`, you can edit the `prompt` to your liking or you can leave it the same as it is.

## make your replicate account

if you do not already have a replicate account, you can make one by going to this link: https://replicate.com

copy .env_example to .env

change the .env file to include your replicate api token.

## ur done

in your browser, connect to the panel by going to https://localhost:5000.

# thanks to
- nickplj12 (for mercenary discord bot, which this is sorta based off of) aka nickplj12 on discord
- Meta (for llama)
- AlphaBlaster
- dotheboogey678 aka vargskelethor_joel on discord
