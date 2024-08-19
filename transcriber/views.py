from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from google.cloud import speech_v1p1beta1 as speech
import io
import librosa
import soundfile as sf
from pydub import AudioSegment
import numpy as np

# Index view to render the HTML page
def index(request):
    return render(request, 'transcriber/index.html')

@csrf_exempt
def transcribe_audio(request):
    if request.method == 'POST':
        audio_file = request.FILES['file']
        content = audio_file.read()

        print(f"Received audio content type: {audio_file.content_type}, size: {len(content)}")

        try:
            # Use pydub to load the audio file
            audio = AudioSegment.from_file(io.BytesIO(content))
            y = np.array(audio.get_array_of_samples())
            sr = audio.frame_rate
            print(f"Loaded with pydub, sample rate: {sr}")

            # Resample to 48000 Hz if it's not already
            if sr != 48000:
                y = librosa.resample(y, orig_sr=sr, target_sr=48000)

            # Save the resampled audio to a buffer in WAV format
            wav_io = io.BytesIO()
            sf.write(wav_io, y, 48000, format='WAV')
            wav_io.seek(0)
            converted_content = wav_io.read()

            print(f"Converted audio content size: {len(converted_content)}")

            # Prepare the audio for transcription
            recognition_audio = speech.RecognitionAudio(content=converted_content)
            config = speech.RecognitionConfig(
                encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
                sample_rate_hertz=48000,
                language_code="en-US",
            )

            # Call the Google Cloud Speech-to-Text API
            client = speech.SpeechClient()
            response = client.recognize(config=config, audio=recognition_audio)

            # Extract the transcript from the response
            transcript = ""
            for result in response.results:
                transcript += result.alternatives[0].transcript

            print(f"Full response: {response}")
            print(f"Transcript: {transcript}")

            return JsonResponse({"transcript": transcript})
        except Exception as e:
            print(f"Error occurred during transcription: {e}")
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request method"}, status=405)
