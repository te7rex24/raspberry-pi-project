#If you want to run this script on your computer, don't forget to download the model from the Vosk website(https://alphacephei.com/vosk/models).
#Don't forget to also change the path on the VOSK model (line 14)
#Install the local AI model using the Ollama programm (https://ollama.com/download/windows) and after installation use the command ( ollama run smollm2:135m )


import queue
import json
import sounddevice as sd
from vosk import Model, KaldiRecognizer
import ollama
import pyttsx3

#VOSK Config
VOSK_MODEL_PATH = "/Users/te7rex/raspberry-pi-project/src/ai/vosk-model-en-us-0.22-lgraph"              # Path to VOSK model
DEVICE = None                                                                                           # Specify the audio input device (None for default device)
SAMPLE_RATE = 16000                                                                                     # Audio sample rate (Never change it)
BLOCK_SIZE = 4096                                                                                       # Define the size of each audio block (Never change it)
CHANNELS = 1                                                                                            # Number of channels (1 - mono, 2 - stereo)
DATA_TYPE = "int16"                                                                                     # Set the data type for audio samples (int16 - CD quality)
#PYTTSX3 Config
RATE = 150                                                                                              # Speed of speech
VOLUME = 0.5                                                                                            # Volume level (0.0 to 1.0)
#OLLAMA Config
OLLAMA_MODEL = "smollm2:135m"                                                                           # Ollama model name 


# Initialize VOSK for speech-to-text
model = Model(VOSK_MODEL_PATH)
recognizer = KaldiRecognizer(model, SAMPLE_RATE)
recognizer.SetWords(True)

# Initialize pyttsx3 for text-to-speech
engine = pyttsx3.init()
engine.setProperty('rate', RATE)
engine.setProperty('volume', VOLUME)

# Queue for audio data
audio_queue = queue.Queue()

def audio_callback(indata, frames, time, status):
    #Callback to capture audio data from the microphone
    audio_queue.put(bytes(indata))

def transcribe_speech():
    #Real-time speech transcription
    print("\nSpeak now... (Press Ctrl+C to exit)")
    transcript = []
    
# Open an audio input stream using sounddevice
    with sd.RawInputStream(
        samplerate = SAMPLE_RATE,
        blocksize = BLOCK_SIZE,  
        device = DEVICE,     
        dtype = DATA_TYPE,        
        channels = CHANNELS,    
        callback = audio_callback  
        ):
    # Start an inf:inite loop to continuously process audio data
        while True:
        # Get the next chunk of audio data from the queue
            data = audio_queue.get()
        
        # Check if the recognizer has finalized the recognition of a speech segment
            if recognizer.AcceptWaveform(data):
            # Load the final recognition result as a JSON object
                result = json.loads(recognizer.Result())
            
            # Check if the result contains recognized text
                if result['text']:
                # Append the recognized text to the transcript list
                    transcript.append(result['text'])
                
                # Print the recognized text to the console
                    print(f"\nRecognized: {result['text']}")
                
                # Return the full transcript as a single string
                    return ' '.join(transcript)
        
        # If the recognizer has not finalized the result, check for partial results
            else:
            # Load the partial recognition result as a JSON object
                partial = json.loads(recognizer.PartialResult())            
            # Check if the partial result contains a "partial" key
                if 'partial' in partial:
                # Print the partial result to the console (on the same line)
                    print(f"\rPartial: {partial['partial']}", end='', flush=True)

def ollama_chat(prompt):
    # Send a prompt to PI_AI and get a response
    print("\nProcessing request...")
    response = ollama.generate(model=OLLAMA_MODEL, prompt=prompt, stream=False,)
    return response['response']

def speak(text):
    # Convert text to speech using pyttsx3
    print(f"\nSpeaking: {text}")
    engine.say(text)
    engine.runAndWait()

def main():
    
    try:
        while True:
            # Speech recognition
            text = transcribe_speech()
            
            # Process text with Ollama
            response = ollama_chat(text)
            
            # Display the result
            print("\nPI_AI's response:")
            print(response)
            
            # Speak the response
            speak(response)
            
    except KeyboardInterrupt:
        print("\nSession ended")

if __name__ == "__main__":
    main()