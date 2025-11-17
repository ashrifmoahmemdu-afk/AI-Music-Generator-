from music21 import note, chord, stream, instrument

def test_short_melody():
    print("Testing short melody...")
    s = stream.Stream()
    notes = ['C4', 'E4', 'G4', 'C5'] * 5
    for i, pitch in enumerate(notes):
        n = note.Note(pitch)
        n.offset = i * 0.3  # Faster tempo
        n.storedInstrument = instrument.Piano()
        s.append(n)
    s.write('midi', fp='test_short.mid')
    print("✓ Created test_short.mid")

def test_chords():
    print("Testing chords...")
    s = stream.Stream()
    chords = ['C4.E4.G4', 'G4.B4.D5', 'F4.A4.C5', 'C4.E4.G4']
    for i, chord_name in enumerate(chords):
        notes_in_chord = chord_name.split('.')
        chord_notes = []
        for pitch in notes_in_chord:
            n = note.Note(pitch)
            n.storedInstrument = instrument.Piano()
            chord_notes.append(n)
        new_chord = chord.Chord(chord_notes)
        new_chord.offset = i * 1.0
        s.append(new_chord)
    s.write('midi', fp='test_chords.mid')
    print("✓ Created test_chords.mid")

def test_fast_music():
    print("Testing fast music...")
    s = stream.Stream()
    # Fast scale run
    notes = ['C4', 'D4', 'E4', 'F4', 'G4', 'A4', 'B4', 'C5', 'B4', 'A4', 'G4', 'F4', 'E4', 'D4', 'C4']
    for i, pitch in enumerate(notes):
        n = note.Note(pitch)
        n.offset = i * 0.2  # Very fast
        n.storedInstrument = instrument.Piano()
        s.append(n)
    s.write('midi', fp='test_fast.mid')
    print("✓ Created test_fast.mid")

# Run all tests
test_short_melody()
test_chords()
test_fast_music()
print("🎵 All test files created!")
print("Check your folder for: test_short.mid, test_chords.mid, test_fast.mid")