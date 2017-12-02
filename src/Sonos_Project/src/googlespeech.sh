#!/bin/bash

command=$1

curl 'https://translate.google.com/translate_tts?ie=UTF-8&q='${command}'&tl=en&client=tw-ob' -H 'Referer: http://translate.google.com/' -H 'User-Agent: stagefright/1.2 (Linux;Android 5.0)' > /Users/ege/eclipse-workspace/Sonos_Project/src/playlists/googletest.mp3

