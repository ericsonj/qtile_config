# Copyright (c) 2020 Ericson Joseph
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import vlc
from libqtile import bar
from libqtile.widget import base
from libqtile.log_utils import logger

__all__ = [
    'Radio',
]

class Radio(base._TextBox):
    """Widget that play radio stream

    For using the radio widget you need to have python-vlc installed (pip install python-vlc).
    You can search your favorite radio station in http://www.radio-browser.info/gui/#!/ and 
    add name and url in playlist dict.
    
    Mouse BUTTON_1: Play/Stop
    Mouse BUTTON_3: Next
    Mouse BUTTON_2: Mute
    Mouse BUTTON_4: Raise volume
    Mouse BUTTON_5: Lower volume

    ::

        # Add Radio
        Radio(playlist={"LATINA": "http://radiolatina.info:7087/;"})

    Supported bar orientations: horizontal only.
    """
    orientations = base.ORIENTATION_HORIZONTAL
    defaults = [
        ("playing_spinner", ["●","●","○"], "Ascii spinner for playing indicator"),
        ("stopped_spinner", ["▶"], "Ascii spinner for playing indicator"),
        ("max_name_len", 10, "Max name length of radio to be display"),
        ("mute_string", "M", "Mute string for display"),
        ("playlist", None, "Play dict of urls, name : url"),
        ("padding", 3, "Padding left and right. Calculated if None."),
        ("update_interval", 0.5, "Update time in seconds."),
    ]

    def __init__(self, **config):
        base._TextBox.__init__(self, '0', width=bar.CALCULATED, **config)
        self.add_defaults(Radio.defaults)
        self.surfaces = {}
        self.vlcInstance = vlc.Instance()
        self.player = self.vlcInstance.media_player_new()
        self.playlistIdx = 0
        self.disCount = 0
        if not self.playlist:
            self.text = 'Radio: Empty playlist'  
        else:
            self.text = 'Radio'

        self.animTick = 0

    def timer_setup(self):
        self.timeout_add(self.update_interval, self.update)

    def button_press(self, x, y, button):
        if button == 2:
            self.cmd_mute_radio()
        elif button == 4:
            self.cmd_raise_volume()
        elif button == 5:
            self.cmd_lower_volume()
        elif button == 1:
            self.cmd_playstop_radio()
        elif button == 3:
            self.cmd_next_radio()

        self.draw()
        self.bar.draw()

    def update(self):
        if not self.playlist:
            return
        radioItem = list(self.playlist)[self.playlistIdx][:self.max_name_len]
        
        if self.player.get_state() == vlc.State.Playing:
            volume = str(self.player.audio_get_volume()) + '%'
            if self.player.audio_get_mute():
                volume = self.mute_string
            label = self.playing_spinner[self.animTick % len(self.playing_spinner)]
            self.text  = f"{label} {radioItem}, V: {volume}"
        elif self.player.get_state() == vlc.State.Stopped:
            label = self.stopped_spinner[self.animTick % len(self.stopped_spinner)]
            self.text  = f"{label} {radioItem} Stopped"
        elif self.player.get_state() == vlc.State.Error:
            self.text  = f"▶ {radioItem} Error"
        elif self.player.get_state() == vlc.State.Ended:
            self.text  = f"▶ {radioItem} Ended"
        elif self.player.get_state() == vlc.State.Opening:
            self.text  = f"▶ {radioItem} Opening"
        else:
            self.text  = f"▶ {radioItem}"
            
        self.draw()
        self.bar.draw()
        self.animTick += 1
        self.timeout_add(self.update_interval, self.update)


    def cmd_mute_radio(self):
        logger.warn('mute_radio')
        if self.player.get_state() == vlc.State.Playing:
            self.player.audio_set_mute(not self.player.audio_get_mute())
    

    def cmd_playstop_radio(self):
        if not self.playlist:
            return
        logger.warn('cmd_playstop_radio')
        if self.player.get_state() == vlc.State.Playing:
            self.player.stop()
        else:
            if self.player.get_media() == None or self.player.get_state() == vlc.State.Ended:
                radioItemKey = list(self.playlist)[self.playlistIdx];
                media = self.vlcInstance.media_new(self.playlist[radioItemKey])
                self.player.set_media(media)
            self.player.play()


    def cmd_next_radio(self):
        if not self.playlist:
            return

        if self.player.get_state() == vlc.State.Opening:
            return
        
        self.playlistIdx += 1
        self.playlistIdx = self.playlistIdx % len(self.playlist)
        
        self.player.stop()
        radioItemKey = list(self.playlist)[self.playlistIdx];
        media=self.vlcInstance.media_new(self.playlist[radioItemKey])
        self.player.set_media(media)
        self.player.play()
    

    def cmd_raise_volume(self):
        self.player.audio_set_volume(self.player.audio_get_volume() + 2)


    def cmd_lower_volume(self):
        self.player.audio_set_volume(self.player.audio_get_volume() - 2)