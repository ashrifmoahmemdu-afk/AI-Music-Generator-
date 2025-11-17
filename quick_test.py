import os
from music21 import note, chord, stream, instrument
import numpy as np

print('=== Quick Test ===')

# Create a simple melody instantly
s = stream.Stream()

# Add notes
notes = ['C4', 'E4', 'G4', 'C5', 'E5', 'G4', 'C5', 'E4']
for i, pitch in enumerate(notes):
    n = note.Note(pitch)
    n.offset = i * 0.5
    n.storedInstrument = instrument.Piano()
    s.append(n)

# Save
s.write('midi', fp='quick_test.mid')
print(' Created quick_test.mid - Play this file!')
