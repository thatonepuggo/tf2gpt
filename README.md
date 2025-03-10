# tf2gpt - epic rcon ai thing!!

a python program which allows other people in source games to ask an AI a
question, and have a TTS respond.

# how to run

you can run tf2gpt on either windows or linux.

## installing dependencies

the web panel requires Deno.
install it by following the installation instructions on [the Deno docs](https://docs.deno.com/runtime/getting_started/installation/).
on linux, you may be able to install Deno with your package manager.

once installed, run `deno i` in the repository's folder.

<details>
<summary>windows</summary>

1. [install python](https://www.python.org/downloads/)
2. create a virtual environment and install dependencies:

```ps1
py -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

3. install [virtual audio cable](https://vb-audio.com/Cable/).

</details>

<details>
<summary>linux</summary>

1. python should already be installed on most distros, however if it isn't,
   install it using your distro's package manager.
2. create a virtual environment and install dependencies:

```sh
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

3. install a pulseaudio-compatible server.
   for example:
    - pulseaudio
    - pipewire-pulse

</details>

## enabling console.log and rcon access

the program needs to read your `console.log` file.

add the following to your launch options:

```
-condebug -conclearlog -usercon
```

then, add these lines to your `cfg/autoexec.cfg`:

```vdf
ip 0.0.0.0
rcon_password dontcarelol // edit this if you want
net_start
```

## configuring the AI

copy `config.example.yaml` to `config.yaml`. in `config.yaml`, you can edit the
`backstory` variable to your liking or you can leave it the same as it is.

however, you should check that the following are correct:

- the `logfile` variable should be where your `console.log` file is (e.g. `/path/to/steamapps/common/Team Fortress 2/tf/console.log`)
- the `v` variable is set to `2`. **if you have an old config, it will not be there at all. please create a new one.**

<details>
<summary>read this if you changed the rcon_password cvar</summary>

you dont have to edit the `rcon_password` cvar since the port for rcon (`27015`)
likely isn't open, but if you did, edit `config.yaml` and change the `password`
variable to your `rcon_password`.

</details>

## make your replicate account

1. if you do not already have a replicate account, you can make one [here](https://replicate.com).
2. copy `.env.example` to `.env`.
3. change the `.env` file to include your replicate api token.

## ur done

in your browser, connect to the panel by going to http://localhost:5000.

note that it is `http`, not `https`. because of this, if you want to connect to
the panel using the steam overlay browser, you will have to manually tell it to
use `http`.

# FAQ

| q                             | a                                                          |
| :---------------------------- | :--------------------------------------------------------- |
| what is the `funnies` folder? | the `funnies` folder is for funny things people have said. |
| it doesn't work!!!            | create an issue and i will try to help you.                |

# thanks to

- noelle (for mercenary discord bot, which this is sorta based off of) AKA *okaagaca* on discord
- psychpayload (also helped with mercenary) AKA *oakertown.fun* on discord
- AlphaBlaster (don't remember why i put him here, he's just cool ig) AKA *alphablaster* on discord
- [silk icons](https://github.com/markjames/famfamfam-silk-icons)
- Meta (for llama)