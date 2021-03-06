from mido import MidiFile, Message, MidiTrack
import mido


mid = mido.MidiFile("mary.mid")
# collect high level midi information
print(mid)
print("Ticks per beat: "+ str(mid.ticks_per_beat))
print("Time in midi file: " + str(mid.length))
meta = {}
events = [[] for x in range(16)]
for track in mid.tracks:
  for msg in track:
    if type(msg) == mido.midifiles.meta.MetaMessage:
      meta[msg.type] = msg.dict()
    else:
      events[msg.channel].append(msg)
max_ticks = 0
for chnl in range(16):
    ticks = sum(msg.time for msg in events[chnl])
    if ticks > max_ticks:
        max_ticks = ticks
print("max ticks: " + str(max_ticks))
try:
    tempo = meta["set_tempo"]["tempo"]
except:
    tempo = 500000
seconds = mido.tick2second(max_ticks, mid.ticks_per_beat, tempo)
print("Total seconds computed: " + str(seconds))

for index, chnl in enumerate(events):
    time = 0
    volume = 0
    note_on = [int(-1) for x in range(128)]
    for msg in chnl:
        if msg.type == "note_on":
#           print("on ", msg.note, "time", time_counter, "duration", msg.time, "velocity", msg.velocity)
            note_on_start_time = time
            note_on_end_time = (time + msg.time)
            volume = msg.velocity

            if note_on[msg.note] == -1:
                note_on[msg.note] = (note_on_end_time, volume)
            else:
                old_end_time = note_on[msg.note][0]
                old_volume = note_on[msg.note][1]
                print(index, msg.note, old_end_time, note_on_end_time, old_volume)
                note_on[msg.note] = (note_on_end_time, old_volume)


        if msg.type == "note_off":
#           print("off", msg.note, "time", time_counter, "duration", msg.time, "velocity", msg.velocity)
            note_off_start_time = time
            note_off_end_time = (time + msg.time)
            note_on_end_time = note_register[msg.note][0]
            volume = note_on[msg.note][1]
            print(index, msg.note, note_on_end_time, note_off_end_time, volume)
                    
            note_on[msg.note] = -1  # reinitialize register

        time += msg.time
 
#    print("Time " + str(index) + ": " + str(time))

out = mido.get_output_names()
port = mido.open_output(out[0])
playing=[]
for msg in mid.play(meta_messages=True):
    print(msg)
    notetype=msg.type
    if (notetype=="note_on") or (notetype=="note_off"):
        if msg.velocity == 0:
            note_type = "note_off";
        playing.append([msg.type,msg.channel,msg.note,msg.velocity,msg.time])
#new = MidiFile()
#track = MidiTrack()
#track.append(Message('program_change', channel=0, program=24, time=0))
#for e in playing:
#   track.append(Message(e[0], channel=e[1], note=e[2], velocity=e[3], time=int(e[4]*new.ticks_per_beat*2)))
#new.tracks.append(track)
#new.save('recreated.mid')
time=[]
for i in range(len(playing)):
    if 'note_off' in playing[i] or playing[i][3] == 0:
#        print('Note off')
        off=1
    else:
        off=0
    time.append(playing[i][4])
realtimelist=[]
realtime=0
for j in time:
        realtime+=j
        realtimelist.append(realtime)

print(realtimelist)
port.close()
