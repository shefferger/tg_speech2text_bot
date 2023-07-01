import io
import fs
import speech_recognition as sr
from pydub import AudioSegment

recognizer = sr.Recognizer()


def transcribe(filename: str, filesystem: fs.opener, lang: str) -> str:
    """
    Transcribing audio from file

    :param filename: Name of file
    :param filesystem: Filesystem (e.g. memoryFS)
    :param lang: Language (en/ru)
    :return: Transcribed text string
    """
    with filesystem.open(path=filename, mode='rb') as file:
        with sr.AudioFile(file) as source:
            audio_text = recognizer.listen(source)
            try:
                text = recognizer.recognize_google(audio_text, language=lang)
                print(text)
                return text
            except sr.exceptions.TranscriptionFailed:
                return 'Error'


def convert_ogg2wav(filename_ogg: str, filesystem: fs.opener, file) -> str:
    """
    Audio converter

    :param filename_ogg: Filename in OGG format
    :param filesystem: FS
    :param file: Byte audio file
    :return: Filename of wav file
    """
    sound = AudioSegment.from_file_using_temporary_files(file=io.BytesIO(file), format='ogg')
    buf = io.BytesIO()
    sound.export(buf, format='wav')
    filename_wav = ''.join(filename_ogg.split('.').pop(-1)) + '.wav'
    with filesystem.open(path=filename_wav, mode='wb') as fd:
        fd.write(buf.getvalue())
    return filename_wav
