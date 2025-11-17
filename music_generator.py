import os
import numpy as np
from music21 import converter, instrument, note, chord, stream
import pickle

print("=== AI Music Generator ===")

class SimpleMusicGenerator:
    def __init__(self):
        self.notes = []
        
    def load_or_create_data(self):
        """Load MIDI files or create sample data"""
        print("Preparing music data...")
        
        # If midi_files folder exists, try to load files
        if os.path.exists("midi_files") and any(file.endswith('.mid') for file in os.listdir("midi_files")):
            print("Loading MIDI files...")
            for file in os.listdir("midi_files"):
                if file.endswith(".mid"):
                    try:
                        midi = converter.parse(os.path.join("midi_files", file))
                        for element in midi.flat.notes:
                            if isinstance(element, note.Note):
                                self.notes.append(str(element.pitch))
                            elif isinstance(element, chord.Chord):
                                self.notes.append('.'.join(str(n) for n in element.normalOrder))
                    except:
                        continue
        else:
            # Create sample training data
            print("Creating sample music data...")
            self.create_sample_data()
            
        print(f"Loaded {len(self.notes)} music notes")
        return self.notes
    
    def create_sample_data(self):
        """Create sample music patterns for training"""
        # C major scale patterns
        scales = [
            ['C4', 'D4', 'E4', 'F4', 'G4', 'A4', 'B4', 'C5'],  # Ascending
            ['C5', 'B4', 'A4', 'G4', 'F4', 'E4', 'D4', 'C4'],  # Descending
        ]
        
        # Common chords in C major
        chords = ['C4.E4.G4', 'D4.F4.A4', 'E4.G4.B4', 'F4.A4.C5', 'G4.B4.D5', 'A4.C5.E5']
        
        # Create varied patterns
        for pattern in scales:
            for _ in range(10):
                self.notes.extend(pattern)
                self.notes.append(np.random.choice(chords))
                
        # Add some random variations
        for _ in range(50):
            self.notes.append(np.random.choice(['C4', 'E4', 'G4', 'C5', 'E5', 'G5']))
            
        print("Created sample music patterns")
    
    def generate_ai_music(self, length=100):
        """Generate music using simple AI patterns"""
        print("Generating AI music...")
        
        if not self.notes:
            self.load_or_create_data()
            
        # Create a new stream
        s = stream.Stream()
        
        # Use the learned patterns to generate music
        current_pattern = self.notes[:10]  # Start with beginning pattern
        
        for i in range(length):
            # Choose next note based on simple probability
            if i < len(current_pattern):
                next_note = current_pattern[i]
            else:
                # Pick randomly from learned notes, favoring recent patterns
                if np.random.random() > 0.7 and len(current_pattern) > 0:
                    next_note = np.random.choice(current_pattern)
                else:
                    next_note = np.random.choice(self.notes)
                
                # Update current pattern
                current_pattern.append(next_note)
                if len(current_pattern) > 8:
                    current_pattern.pop(0)
            
            # Add note or chord to stream
            if '.' in next_note:  # It's a chord
                notes_in_chord = next_note.split('.')
                chord_notes = []
                for pitch in notes_in_chord:
                    try:
                        n = note.Note(int(pitch))
                    except:
                        n = note.Note(pitch)
                    n.storedInstrument = instrument.Piano()
                    chord_notes.append(n)
                new_chord = chord.Chord(chord_notes)
                new_chord.offset = i * 0.5
                s.append(new_chord)
            else:  # It's a single note
                try:
                    n = note.Note(next_note)
                    n.offset = i * 0.5
                    n.storedInstrument = instrument.Piano()
                    s.append(n)
                except:
                    # Fallback to middle C if note creation fails
                    n = note.Note('C4')
                    n.offset = i * 0.5
                    n.storedInstrument = instrument.Piano()
                    s.append(n)
            
            # Show progress
            if i % 20 == 0:
                print(f"Generated {i}/{length} notes...")
        
        # Save the generated music
        s.write('midi', fp='ai_music.mid')
        print("✓ AI music generated: ai_music.mid")

# Create and run the generator
generator = SimpleMusicGenerator()
generator.generate_ai_music(length=80)

print("🎵 Done! Play 'ai_music.mid' to hear your AI-generated music!")
print("You can add MIDI files to the 'midi_files' folder for better results.")