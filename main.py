import queue, w, vosk, json
import sounddevice as sd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.linear_model import LogisticRegression
from s import *

q = queue.Queue()

model = vosk.Model('small_model')
device = sd.default.device #default device
samplerate = int(sd.query_devices(device[0], 'input')['default_samplerate'])


def callback(indata, frames, time, status):
    q.put(bytes(indata))
    
    
def recognize(json_d, vectorizer, clf):
    trg = w.NAMES.intersection(json_d.split())
    if not trg:
        return    
    json_d.replace(list(trg)[0], '')
    vector_text = vectorizer.transform([json_d]).toarray()[0]
    answer = clf.predict([vector_text])[0]
    func_name = answer.split()[0]
    speaker(answer.replace(func_name, ''))
    exec(func_name + '()')
    

#listening
def main():
    vectorizer = CountVectorizer()
    vectors = vectorizer.fit_transform(list(w.set_data.keys()))
    clf = LogisticRegression()
    clf.fit(vectors, list(w.set_data.values()))
    del w.set_data
    with sd.RawInputStream(samplerate=samplerate, blocksize = 48000, device=device[0], dtype='int16',
                            channels=1, callback=callback):
            rec = vosk.KaldiRecognizer(model, samplerate)
            while True:
                data = q.get()
                if rec.AcceptWaveform(data):
                    json_d = json.loads(rec.Result())['text']
                    recognize(json_d, vectorizer, clf)


speak("Привет! Я голосовой помощник Диана. Я могу рассказать о себе, если ты об это попросишь.")
 

if __name__ == '__main__':
    main()