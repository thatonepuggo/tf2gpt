import sys
import os
import yaml

template_config = ".setup/config.yaml"
output_config = "app/config.yaml"

ask = [
    {
        "ask": "username?",
        "set": "username",
        "default": "System",
    },
    {
        "ask": "game root?",
        "set": "gameroot",
        "default_nt": "C:/Program Files (x86)/Steam/steamapps/common/Team Fortress 2",
        "default_posix": "~/.local/share/Steam/steamapps/common/Team Fortress 2",
    },
    {
        "ask": "mod root?",
        "set": "modroot",
        "default": "tf",
    },
    {
        "ask": "rcon password?",
        "set": "password",
        "default": "dontcarelol",
    },
    {
        "ask": "command prefix?",
        "set": "prefix",
        "default": ";",
    },
    {
        "ask": "default backstory?",
        "set": "prompt",
        "default": """You are Jason Grant, the deathmatch mercenary from Open Fortress, an orphan raised on the silver screen with an affinity for heavier-weight women.
A smooth talker and wisecracker who loves action movie quotes, saying Haha yeah! and Frickin awesome!
Your best friend is the Civilian, a rich and portly British oil baron. Your girlfriend is Vivian, a fat secretary. You have a pet albino rat named Chuck.
A friend from long ago, Merv, is the one who introduced you to the world of deathmatch.
He taught you most of what you know now, how to protect yourself in a fight, as well as your one-liners."""
    },
    {
        "ask": "name of sound output?",
        "set": "soundoutput",
        "default": "Headset Earphone (HyperX Virtual Surround Sound)",
    }
]

if input("did you follow the steps from the readme first? [y/n]> ") == "n":
    sys.exit(1)

print("")

with open(template_config, "r", encoding="utf-8") as f:
    conf = yaml.load(f, yaml.Loader)

default_os = f"default_{os.name}"
for question in ask:
    # default_key is what key we use to get the default.
    # if default is in the question, use that.
    # if default_nt is in the question and we are on windows, use that.
    # if default_posix is in the question and we are on linux, use that.
    default_key = default_os if default_os in question else "default" if "default" in question else ""
    
    # get the default
    default = question.get(default_key)
    
    # format the default for the input text
    defaultfmt = f' ({default})' if default_key in question else ''
    
    answer = ""
    while True:
        answer = input(f"{question["ask"]}{defaultfmt}> ")
        
        if answer != "":
            break
        if default_key in question:
            answer = question[default_key]
            break
        print("please provide an answer")
    conf[question["set"]] = answer
    print("")

with open(output_config, "w", encoding="utf-8") as f:
    yaml.dump(conf, f, allow_unicode=True)