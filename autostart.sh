#!/bin/sh

# Poweroff laptop screen
xrandr --output eDP-1 --off

#Block screen
systemctl --user start xscreensaver.service

~/.config/qtile/lightson+ -d 2 &

# Random wallpaper
feh --bg-fill --randomize ~/Pictures/backgrounds/ 
