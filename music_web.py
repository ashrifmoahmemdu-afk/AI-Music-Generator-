from flask import Flask, render_template_string, request, send_file, jsonify
import os
import numpy as np
from music21 import note, chord, stream, instrument
import threading
import webbrowser
import time

app = Flask(__name__)

# HTML template for the web interface
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Music Generator</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Arial', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 800px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        
        .header {
            background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }
        
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        
        .header p {
            font-size: 1.2em;
            opacity: 0.9;
        }
        
        .content {
            padding: 30px;
        }
        
        .control-panel {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
        }
        
        .btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 25px;
            cursor: pointer;
            font-size: 16px;
            margin: 5px;
            transition: all 0.3s ease;
        }
        
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(0,0,0,0.2);
        }
        
        .btn:active {
            transform: translateY(0);
        }
        
        .music-type {
            background: #e9ecef;
            padding: 15px;
            border-radius: 8px;
            margin: 10px 0;
        }
        
        .file-list {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 8px;
            margin-top: 20px;
        }
        
        .file-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 10px;
            border-bottom: 1px solid #dee2e6;
        }
        
        .file-item:last-child {
            border-bottom: none;
        }
        
        .status {
            padding: 10px;
            border-radius: 5px;
            margin: 10px 0;
            text-align: center;
            font-weight: bold;
        }
        
        .status.success {
            background: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }
        
        .status.error {
            background: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }
        
        .status.info {
            background: #cce7ff;
            color: #004085;
            border: 1px solid #b3d7ff;
        }
        
        .slider-container {
            margin: 15px 0;
        }
        
        .slider-container label {
            display: block;
            margin-bottom: 5px;
            font-weight: bold;
        }
        
        input[type="range"] {
            width: 100%;
            margin: 10px 0;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎵 AI Music Generator</h1>
            <p>Create beautiful music with artificial intelligence</p>
        </div>
        
        <div class="content">
            <div class="control-panel">
                <h2>🎹 Generate Music</h2>
                
                <div class="music-type">
                    <h3>Quick Demos</h3>
                    <button class="btn" onclick="generateMusic('quick')">
                        🎼 Quick Melody
                    </button>
                    <button class="btn" onclick="generateMusic('chords')">
                        🎶 Chord Progression
                    </button>
                    <button class="btn" onclick="generateMusic('fast')">
                        ⚡ Fast Scale
                    </button>
                </div>
                
                <div class="music-type">
                    <h3>AI Music</h3>
                    <div class="slider-container">
                        <label for="length">Number of Notes: <span id="lengthValue">50</span></label>
                        <input type="range" id="length" min="10" max="200" value="50" oninput="updateLengthValue(this.value)">
                    </div>
                    <button class="btn" onclick="generateAIMusic()">
                        🤖 Generate AI Music
                    </button>
                </div>
                
                <div class="music-type">
                    <h3>Music Styles</h3>
                    <button class="btn" onclick="generateMusic('happy')">
                        😊 Happy Melody
                    </button>
                    <button class="btn" onclick="generateMusic('sad')">
                        😢 Sad Melody
                    </button>
                    <button class="btn" onclick="generateMusic('epic')">
                        🎻 Epic Theme
                    </button>
                </div>
            </div>
            
            <div id="status"></div>
            
            <div class="file-list">
                <h2>📁 Your Music Files</h2>
                <button class="btn" onclick="refreshFiles()">
                    🔄 Refresh List
                </button>
                <div id="fileList">
                    Loading files...
                </div>
            </div>
            
            <div class="music-type">
                <h3>🎧 How to Play</h3>
                <p>1. Click "Download" next to any file</p>
                <p>2. Double-click the .mid file to play</p>
                <p>3. Or upload to <a href="https://onlinesequencer.net/" target="_blank">Online Sequencer</a></p>
            </div>
        </div>
    </div>

    <script>
        function updateLengthValue(value) {
            document.getElementById('lengthValue').textContent = value;
        }
        
        function showStatus(message, type) {
            const statusDiv = document.getElementById('status');
            statusDiv.innerHTML = `<div class="status ${type}">${message}</div>`;
            setTimeout(() => {
                statusDiv.innerHTML = '';
            }, 5000);
        }
        
        function generateMusic(type) {
            showStatus('🎵 Generating music...', 'info');
            
            fetch('/generate/' + type)
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        showStatus('✅ ' + data.message, 'success');
                        refreshFiles();
                    } else {
                        showStatus('❌ ' + data.message, 'error');
                    }
                })
                .catch(error => {
                    showStatus('❌ Error: ' + error, 'error');
                });
        }
        
        function generateAIMusic() {
            const length = document.getElementById('length').value;
            showStatus('🤖 AI is composing...', 'info');
            
            fetch('/generate/ai?length=' + length)
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        showStatus('✅ ' + data.message, 'success');
                        refreshFiles();
                    } else {
                        showStatus('❌ ' + data.message, 'error');
                    }
                })
                .catch(error => {
                    showStatus('❌ Error: ' + error, 'error');
                });
        }
        
        function refreshFiles() {
            fetch('/files')
                .then(response => response.json())
                .then(files => {
                    const fileList = document.getElementById('fileList');
                    if (files.length === 0) {
                        fileList.innerHTML = '<p>No music files yet. Generate some music!</p>';
                        return;
                    }
                    
                    fileList.innerHTML = files.map(file => `
                        <div class="file-item">
                            <span>🎵 ${file}</span>
                            <a href="/download/${file}" class="btn" download>📥 Download</a>
                        </div>
                    `).join('');
                });
        }
        
        function downloadFile(filename) {
            window.location.href = '/download/' + filename;
        }
        
        // Load files when page loads
        window.onload = refreshFiles;
    </script>
</body>
</html>
'''

class MusicGenerator:
    def __init__(self):
        self.output_dir = "web_music"
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
    
    def generate_quick_melody(self):
        s = stream.Stream()
        notes = ['C4', 'E4', 'G4', 'C5', 'E5', 'G4', 'C5', 'E4']
        for i, pitch in enumerate(notes):
            n = note.Note(pitch)
            n.offset = i * 0.5
            n.storedInstrument = instrument.Piano()
            s.append(n)
        filename = "quick_melody.mid"
        s.write('midi', fp=os.path.join(self.output_dir, filename))
        return filename
    
    def generate_chords(self):
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
            new_chord.offset = i * 2.0
            s.append(new_chord)
        filename = "chord_progression.mid"
        s.write('midi', fp=os.path.join(self.output_dir, filename))
        return filename
    
    def generate_fast_scale(self):
        s = stream.Stream()
        notes = ['C4', 'D4', 'E4', 'F4', 'G4', 'A4', 'B4', 'C5', 'B4', 'A4', 'G4', 'F4', 'E4', 'D4', 'C4']
        for i, pitch in enumerate(notes):
            n = note.Note(pitch)
            n.offset = i * 0.2
            n.storedInstrument = instrument.Piano()
            s.append(n)
        filename = "fast_scale.mid"
        s.write('midi', fp=os.path.join(self.output_dir, filename))
        return filename
    
    def generate_happy_melody(self):
        s = stream.Stream()
        notes = ['C4', 'E4', 'G4', 'C5', 'E5', 'G5', 'E5', 'C5', 'G4', 'E4', 'C4']
        for i, pitch in enumerate(notes):
            n = note.Note(pitch)
            n.offset = i * 0.4
            n.storedInstrument = instrument.Piano()
            s.append(n)
        filename = "happy_melody.mid"
        s.write('midi', fp=os.path.join(self.output_dir, filename))
        return filename
    
    def generate_sad_melody(self):
        s = stream.Stream()
        notes = ['C4', 'D4', 'F4', 'G4', 'A4', 'G4', 'F4', 'D4', 'C4']
        for i, pitch in enumerate(notes):
            n = note.Note(pitch)
            n.offset = i * 0.6
            n.storedInstrument = instrument.Piano()
            s.append(n)
        filename = "sad_melody.mid"
        s.write('midi', fp=os.path.join(self.output_dir, filename))
        return filename
    
    def generate_epic_theme(self):
        s = stream.Stream()
        # Epic chord progression
        chords = [
            'C3.G3.C4.E4',
            'G3.D4.G4.B4', 
            'A3.E4.A4.C5',
            'F3.C4.F4.A4'
        ]
        for i, chord_name in enumerate(chords):
            notes_in_chord = chord_name.split('.')
            chord_notes = []
            for pitch in notes_in_chord:
                n = note.Note(pitch)
                n.storedInstrument = instrument.Piano()
                chord_notes.append(n)
            new_chord = chord.Chord(chord_notes)
            new_chord.offset = i * 3.0
            s.append(new_chord)
        filename = "epic_theme.mid"
        s.write('midi', fp=os.path.join(self.output_dir, filename))
        return filename
    
    def generate_ai_music(self, length=50):
        s = stream.Stream()
        
        # AI-like pattern with variations
        base_pattern = ['C4', 'E4', 'G4', 'C5', 'E5', 'G4', 'C5', 'E4']
        patterns = [
            base_pattern,
            ['G4', 'B4', 'D5', 'G5', 'B4', 'D5', 'G5', 'B4'],
            ['F4', 'A4', 'C5', 'F5', 'A4', 'C5', 'F5', 'A4']
        ]
        
        for i in range(length):
            pattern = patterns[i % len(patterns)]
            note_index = (i + (i // 8)) % len(pattern)
            pitch = pattern[note_index]
            
            # Add some randomness
            if np.random.random() < 0.2:
                pitch = pattern[np.random.randint(len(pattern))]
            
            n = note.Note(pitch)
            n.offset = i * 0.5
            n.storedInstrument = instrument.Piano()
            s.append(n)
        
        filename = f"ai_music_{length}notes.mid"
        s.write('midi', fp=os.path.join(self.output_dir, filename))
        return filename

# Create generator instance
music_gen = MusicGenerator()

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/generate/<music_type>')
def generate_music(music_type):
    try:
        if music_type == 'quick':
            filename = music_gen.generate_quick_melody()
            message = f"Quick melody generated: {filename}"
        elif music_type == 'chords':
            filename = music_gen.generate_chords()
            message = f"Chord progression generated: {filename}"
        elif music_type == 'fast':
            filename = music_gen.generate_fast_scale()
            message = f"Fast scale generated: {filename}"
        elif music_type == 'happy':
            filename = music_gen.generate_happy_melody()
            message = f"Happy melody generated: {filename}"
        elif music_type == 'sad':
            filename = music_gen.generate_sad_melody()
            message = f"Sad melody generated: {filename}"
        elif music_type == 'epic':
            filename = music_gen.generate_epic_theme()
            message = f"Epic theme generated: {filename}"
        else:
            return jsonify({'success': False, 'message': 'Unknown music type'})
        
        return jsonify({'success': True, 'message': message, 'filename': filename})
    
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'})

@app.route('/generate/ai')
def generate_ai_music():
    try:
        length = request.args.get('length', 50, type=int)
        filename = music_gen.generate_ai_music(length)
        message = f"AI music generated with {length} notes: {filename}"
        return jsonify({'success': True, 'message': message, 'filename': filename})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'})

@app.route('/files')
def list_files():
    try:
        files = [f for f in os.listdir(music_gen.output_dir) if f.endswith('.mid')]
        return jsonify(files)
    except Exception as e:
        return jsonify([])

@app.route('/download/<filename>')
def download_file(filename):
    try:
        return send_file(
            os.path.join(music_gen.output_dir, filename),
            as_attachment=True,
            download_name=filename
        )
    except Exception as e:
        return f"Error: {str(e)}", 404

def open_browser():
    time.sleep(2)
    webbrowser.open('http://127.0.0.1:5000')

if __name__ == '__main__':
    print("🎵 Starting AI Music Generator Web Interface...")
    print("🌐 Opening browser automatically...")
    print("📁 Music files will be saved in 'web_music' folder")
    print("🚀 Server running at: http://127.0.0.1:5000")
    print("⏹️  Press Ctrl+C to stop the server")
    
    # Open browser automatically
    threading.Thread(target=open_browser).start()
    
    # Run the Flask app
    app.run(debug=True, use_reloader=False)