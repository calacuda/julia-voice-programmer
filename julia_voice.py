#!/bin/env python
"""
an app that alows you to program in a julia repl with your voice
"""


#import deepspeech as ds
import easy_pyttsx3 as pt
import asyncio
import pty
import os
from subprocess import run
import re


pass_file = "/tmp/julia-voice-programmer.txt"
hist_file = pass_file[:-4]+"_hist.txt"
err_file = pass_file[:-4]+"_err.txt"

after_header = False

tmux_sess = "julia-voice"
#shell = f"tmux -L \"{tmux_sess}\" new-session -s \"{tmux_sess}\" -n \"{tmux_sess}\"julia"
shell = "julia"
ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')


def speak(utterance):
    """
    says uterance curently a wrapper for pt.say() so this can be integrated with mycroft
    later.
    """
    if utterance:
        #print("utterance : ", utterance)
        pt.say(utterance)
    #print("utterance : ", utterance)
    #os.system(f"echo \"{utterance}\" | festival --tts")
    #run(f"echo \"{utterance}\" | festival --tts ", shell=True)
    

def get_speakable():
    with open(pass_file, 'r') as df:
        lines = []
        text = df.read()
        #if text.replace(" ", "")[-7:-1] == "julia>":
            
            #for line in text.split("\n")[-1::-1]:
            #    #if line != " ":
            #    if (line[0:6] != "julia>") and not (len(line) > 1 and line[0].isalpha()):
            #        print(f"apending : ", line)
            #        lines.append(line)
            #    if ("julia>" in line) and (len(lines) > 1):
            #        print("breaking", line)
            #        break
                        
        #for line in df.readlines()[::-1]:
        #    if line[0:6] != "julia>" and not (len(line) > 1 and line[0].isalpha()):
        #        lines.append(line) # .replace("(", " ").replace(")", " "))
        #    if ("julia>" in line) and (len(lines) > 1):
        #        break
        #return lines[::-1]
        if text[-7:-1] == "julia>":
            special_car = re.compile(r"_|-|\||\\|\n|/|'|\t|`|\([^)]*\)|\s*\|.*")
            lines = re.split("julia>", text) #text.split("julia>")
            for line in lines[::-1]:
                if (line != " ") and (line != "\n") and line and special_car.sub("", line).replace(" ", ""):
                    #print("line\n", special_car.sub("", line).replace(" ", ""), "\nline")
                    #print(lines[::-1])
                    speakable = line.split("\n")
                    #print("sepak\n", speakable, "\nspeak")
                    return speakable if speakable[1][0:6] != "ERROR:" else speakable[0:2] 
        return [""]

        
def verbalize():
    """
    speaks the code output.
    """
    lines = get_speakable()
    if len(lines) > 0:
        #print("speaking")
        speak("; ".join(lines))


def read(fd):
    data = os.read(fd, 1024)
    readable = ansi_escape.sub('', data.decode("utf-8"))
    bare = readable.replace("\r", "")
    if bare[0:6].replace("julia>", " "):
        with open(pass_file, 'a') as pf:
            pf.write(bare) # + "\n" if bare else "")
        with open(hist_file, 'a') as hf:
            hf.write(readable)
    else:
        with open(pass_file, 'w') as pf:
            pass
    verbalize()
    return data

with open(pass_file, "w") as pf:
    pass

pty.spawn(shell, read)
#print("\n\n<ended>\n\n")
