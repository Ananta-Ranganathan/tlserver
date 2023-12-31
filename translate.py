from transformers import SeamlessM4Tv2Model, AutoProcessor
import torchaudio
import asyncio

# processor = AutoProcessor.from_pretrained("facebook/seamless-m4t-v2-large")
# model = SeamlessM4Tv2Model.from_pretrained("facebook/seamless-m4t-v2-large")
# processor.save_pretrained("seamless")
# model.save_pretrained("seamless")
processor = AutoProcessor.from_pretrained("seamless", local_files_only=True)
model = SeamlessM4Tv2Model.from_pretrained("seamless", local_files_only=True)


async def translate(file):
    print("Translating")
    audio, orig_freq = torchaudio.load(file)
    print("Audio loaded")
    audio =  torchaudio.functional.resample(audio, orig_freq=orig_freq, new_freq=16_000)
    print("Audio resampled")
    audio_inputs = processor(audios=audio, return_tensors="pt", sampling_rate=16_000)
    print("Audio processed")
    output_tokens = model.generate(**audio_inputs, tgt_lang="eng", generate_speech=False)
    print("Translation generated")
    transcription = processor.decode(output_tokens[0].tolist()[0], skip_special_tokens=True)
    print("Transcription decoded")
    return transcription

async def main():
    print(await translate("test.wav"))

if __name__ == "__main__":
    asyncio.run(main())