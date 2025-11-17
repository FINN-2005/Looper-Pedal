import sounddevice as sd
import numpy as np
import keyboard
from collections import deque

# Audio settings
SAMPLE_RATE = 44100
CHANNELS = 1
BLOCK_SIZE = 2048

class LoopPedal:
    def __init__(self, delay_ms=100):  # Add delay parameter with default 100ms
        self.recording = False
        self.overdubbing = False
        self.loop_data = None
        self.temp_recording = None
        self.current_position = 0
        self.loop_length = None  # Store the fixed length of the loop
        
        # Simpler delay implementation using deque
        self.delay_samples = int(SAMPLE_RATE * delay_ms / 1000)
        self.delay_buffer = deque([0] * self.delay_samples, maxlen=self.delay_samples)
        
    def audio_callback(self, indata, outdata, frames, time, status):
        if status:
            print(status)
        
        # Handle delay buffer
        input_data = indata[:, 0]
        delayed_data = np.zeros(frames)
        
        # Process each sample through delay buffer
        for i in range(frames):
            delayed_data[i] = self.delay_buffer[0]  # Get oldest sample
            self.delay_buffer.append(input_data[i])  # Add new sazmple
        
        # First Recording - sets the loop length
        if self.recording and self.loop_data is None:
            if self.temp_recording is None:
                self.temp_recording = delayed_data.copy()
            else:
                self.temp_recording = np.append(self.temp_recording, delayed_data)
            outdata.fill(0)
            return

        # Only proceed with position checks if we have a loop
        if self.loop_data is not None:
            # Overdubbing with fixed length
            if self.overdubbing:
                remaining = self.loop_length - self.current_position
                if remaining >= frames:
                    outdata[:, 0] = self.loop_data[self.current_position:self.current_position + frames]
                    self.loop_data[self.current_position:self.current_position + frames] += delayed_data * 0.7
                    self.current_position += frames
                else:
                    outdata[:remaining, 0] = self.loop_data[self.current_position:]
                    outdata[remaining:, 0] = self.loop_data[:frames-remaining]
                    self.loop_data[self.current_position:] += delayed_data[:remaining] * 0.7
                    self.loop_data[:frames-remaining] += delayed_data[remaining:] * 0.7
                    self.current_position = frames - remaining
            else:
                # Playback only (unchanged)
                remaining = self.loop_length - self.current_position
                if remaining >= frames:
                    outdata[:, 0] = self.loop_data[self.current_position:self.current_position + frames]
                    self.current_position += frames
                else:
                    outdata[:remaining, 0] = self.loop_data[self.current_position:]
                    outdata[remaining:, 0] = self.loop_data[:frames-remaining]
                    self.current_position = frames - remaining

            if self.current_position >= self.loop_length:
                self.current_position = 0
        else:
            outdata.fill(0)

    def toggle_recording(self):
        if self.loop_data is None:
            if not self.recording:  # Start first recording
                self.recording = True
                self.temp_recording = None
                print("Recording first loop...")
            else:  # Stop first recording and set loop length
                self.recording = False
                self.loop_data = self.temp_recording
                self.loop_length = len(self.loop_data)
                self.temp_recording = None
                print(f"First loop recorded: {self.loop_length/SAMPLE_RATE:.2f} seconds")
        else:
            # Toggle between overdub and playback mode
            self.overdubbing = not self.overdubbing
            print("Recording enabled" if self.overdubbing else "Recording disabled - Playback only")

    def clear_loop(self):
        self.loop_data = None
        self.temp_recording = None
        self.current_position = 0
        self.recording = False
        self.overdubbing = False
        self.loop_length = None
        print("Loop cleared")

def main():
    looper = LoopPedal(delay_ms=180)  # Set to match the high input latency

    print("Overdub Looper Pedal Started")
    print("Press SPACE to record/overdub")
    print("Press C to clear loop")
    print("Press Q to quit")
    
    with sd.Stream(channels=CHANNELS,
                  samplerate=SAMPLE_RATE,
                  blocksize=BLOCK_SIZE,
                  callback=looper.audio_callback):
        
        while True:
            if keyboard.is_pressed('space'):
                looper.toggle_recording()
                while keyboard.is_pressed('space'): pass  # Debounce
                
            if keyboard.is_pressed('c'):
                looper.clear_loop()
                while keyboard.is_pressed('c'): pass  # Debounce
                
            if keyboard.is_pressed('q'):
                print("Quitting...")
                break

if __name__ == "__main__":
    main()
