#!/usr/bin/env python3

# Coloring Music project for SRP: RR_2/24/21
# Read MIDI input of music pieces and transform them into
# visual representation using color schemes


import sys
import mido
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib.colors import colorConverter as colorConverter
from matplotlib import animation as animation

# modify MidiFile class originally from library: mido


class MidiFile(mido.MidiFile):

    # input: name of demo midi file
    # input: whether to animate
    def __init__(self, filename, animate=True):
        mido.MidiFile.__init__(self, filename)
        self.meta = {}
        self.events = self.get_events()
        # build and set fig obj
        plt.ioff()
        self.fig = plt.figure(figsize=(8, 6))
        self.fig.canvas.set_window_title("Coloring Music for SRP")
        self.axes = self.fig.add_subplot(111)
        self.axes.axis("equal")
        self.axes.set_facecolor("black")

        if animate is True:
            self.axes.axis([0, 400, 20, 100])
            self.ani = animation.FuncAnimation(self.fig, self.update, interval=50,
                                               init_func=self.draw_time_scale, blit=False)
        else:
            self.draw_time_scale(animate)
        plt.draw()
        plt.ion()
        plt.show(block=True)

    def update(self, i):
        # print(i)
        left, right = self.axes.get_xlim()
        self.axes.set_xlim(left + 10, right + 10)

    def get_events(self):
        mid = self
#        print(mid)

        # support upto 16 channels
        events = [[] for x in range(16)]

        for track in mid.tracks:
            for msg in track:
                try:
                    channel = msg.channel
                    events[channel].append(msg)
                except AttributeError:
                    try:
                        if type(msg) != type(mido.UnknownMetaMessage):
                            self.meta[msg.type] = msg.dict()
                        else:
                            pass
                    except:
                        print("error in MIDI file", type(msg))
        return events

    def get_time_scale(self):
        events = self.get_events()

        # the numpy array needs memory allocated
        time_scale = np.zeros((16, 128, self.get_time_in_ticks()), dtype="int8")

        # state: on/off
        # save inside register array for each piano/instrument note played
        note_register = [int(-1) for x in range(128)]

        # declare a register array: save state(program_change) for every channel
        timbre_register = [1 for x in range(16)]

        for idx, channel in enumerate(events):
            time = 0
            volume = 100
            # Volume would change by control change event (cc) cc7 & cc11
            # Volume 0-100 is mapped to 0-127

            print("channel #", idx, "start")
            for msg in channel:
                if msg.type == "control_change":
                    if msg.control == 7:
                        volume = msg.value
                        # directly assign volume
                    if msg.control == 11:
                        volume = volume * msg.value // 127
                        # change volume by percentage
                    # print("cc", msg.control, msg.value, "duration", msg.time)

                if msg.type == "program_change":
                    timbre_register[idx] = msg.program
                    print("channel", idx, "_pc", msg.program,
                          "_time", time, "_duration", msg.time)

                if msg.type == "note_on":
                    print("on ", msg.note, "_time", time, "_duration",
                          msg.time, "_velocity", msg.velocity)
                    note_on_end_time = (time + msg.time)
                    intensity = volume * msg.velocity // 127
                    # The music note will begin playing when a "note_on" event *ends*
                    # If there is no value iniside the register, Record it as end
                    # time of "note_on" event
		            # Fill in color only when "note_off" event happens
                    if note_register[msg.note] == -1:
                        note_register[msg.note] = (
                            note_on_end_time, intensity)
                    else:
			# Also have to fill in the color when note_on event happens again
                        prev_end_time = note_register[msg.note][0]
                        prev_intensity = note_register[msg.note][1]
                        time_scale[idx, msg.note,
                             prev_end_time: note_on_end_time] = prev_intensity
                        note_register[msg.note] = (
                            note_on_end_time, intensity)

                if msg.type == "note_off":
                    print("off", msg.note, "_time", time, "_duration",
                          msg.time, "_velocity", msg.velocity)
                    note_off_end_time = (time + msg.time)
                    note_on_end_time = note_register[msg.note][0]
                    intensity = note_register[msg.note][1]
		            # fill in color
                    time_scale[idx, msg.note,
                         note_on_end_time:note_off_end_time] = intensity

                    note_register[msg.note] = -1  # reinitialize register

                time += msg.time

            # close any note if it is still open at the end of the channel
            for key, data in enumerate(note_register):
                if data != -1:
                    note_on_end_time = data[0]
                    intensity = data[1]
                    time_scale[idx, key, note_on_end_time:] = intensity
                note_register[idx] = -1
        return time_scale

    def draw_time_scale(self, animate=True):

        time_scale = self.get_time_scale()

        # convert time units from tick -> second
        tick = self.get_time_in_ticks()
        second = mido.tick2second(
            tick, self.ticks_per_beat, self.get_tempo())
#        print(second)
        if second > 10:
            x_label_period_sec = second // 10
        else:
            x_label_period_sec = second / 10  # milliseconds
#        print(x_label_period_sec)
        x_label_interval = mido.second2tick(
            x_label_period_sec, self.ticks_per_beat, self.get_tempo())
        if animate is False:
            plt.xticks([int(x * x_label_interval) for x in range(20)],
                       [round(x * x_label_period_sec, 2) for x in range(20)])

        # modify label and scale of y axis
        plt.yticks([y*16 for y in range(8)], [y*16 for y in range(8)])

        channel_nb = 16
        transparent = colorConverter.to_rgba('black')
        colors = [mpl.colors.to_rgba(mpl.colors.hsv_to_rgb(
            (i / channel_nb, 1, 1)), alpha=1) for i in range(channel_nb)]
        cmaps = [mpl.colors.LinearSegmentedColormap.from_list('my_cmap',
            [transparent, colors[i]], 128) for i in range(channel_nb)]

        # get a color for each channel
        for i in range(channel_nb):
            cmaps[i]._init()
            # create your alpha array and fill the colormap with them.
            alphas = np.linspace(0, 1, cmaps[i].N + 3)
            # create the _lut array, with rgba values
            cmaps[i]._lut[:, -1] = alphas

        # draw notes in time sacle
        for i in range(channel_nb):
            try:
                self.axes.imshow(
                    time_scale[i], origin="lower", interpolation='nearest',
                    cmap=cmaps[i], aspect='auto')
            except IndexError:
                pass

    def get_tempo(self):
        try:
            return self.meta["set_tempo"]["tempo"]
        except:
            #default to 500000 when not specified
            return 500000

    def get_time_in_ticks(self):
        max_ticks = 0
        for channel in range(16):
            ticks = sum(msg.time for msg in self.events[channel])
            if ticks > max_ticks:
                max_ticks = ticks
        return max_ticks


if __name__ == "__main__":
    if len(sys.argv) > 1:
        animate = True
        if len(sys.argv) > 2:
            animate = False
        MidiFile(sys.argv[1], animate)
    else:
        print("Usage: {0} <midi file> [no_animate]".format(sys.argv[0]))
