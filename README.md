# Super Simple Video Subtitle Generator


### get started
- open command prompt (If you don't know how to do this...you should know how to do this...)
  - Ask chatgpt (How to open terminal detailed instruction for windows / mac / linux)
- run `git clone https://github.com/zhangxingeng/auto_generate_video_subtitle_using_openai_wisper.git`
- run `pip install -r requirements.txt` to setup the environment
- find the language you want the subtitles to be translated to lets call it `<lang>`
  - Example of `<lang>`: `en`: english, `de`: german, `ru`: russian, `ja`: japanese, etcs
- to see all languages, just run `python main.py --list_lang`
- one you found your language, run `python main.py lang=<lang>` to generate folder for your video
  - Example: `python main.py lang=en` for english
- Now you should find empty foler `data/<lang>`
- put your video files in folder, recursive folder is fine
- run `python main.py lang=<lang>` to start generating subtitles (it will take quite a wile depending on the length of the video, and your GPU speed)
- wait for tts files show up in the same directory!

### TODOs
- For me personal use so no extra features like keep record of what is generated and start from where it left off, will add it if I got more github stars.
- you can covert tts to other format easily online.


## Acknowledgments
- This project uses OpenAI's Whisper model, which is an open-source machine learning model for speech recognition. 
- The model can be found at [OpenAI's official Whisper repository](https://github.com/openai/whisper) 
- The model is used under the terms of its [MIT License](https://github.com/openai/whisper/blob/main/LICENSE).

## License
- This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details. 
- Components of this project are derived from OpenAI's Whisper model, which is under the MIT license.
