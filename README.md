This project can monitor past broadcasts from broadcastify and download them for analysis and transciption.

This happens in three parts:

  1. A broadcastify feed is continually monitored for the latest archive publications. When a new archive is published (Every 30 min) the MP3 is automatically downloaded.
  
  2. After an MP3 is downloaded it is scrubbed to remove all silent portions of the audio and all volume levels are normalized. This improves transcription speeds and accuracy
  
  3. Modified MP3 is then Transcripted and analyzed by OpenAI's Whisper. All relevant information is retained in both JSON and CSV format. FOr more info on whisper you can find the project here: https://github.com/openai/whisper
  

To collect past broadcasts a premium membership to https://www.broadcastify.com/ is required. Once acquired, simply sign into Broadcastify in the web and copy the cookies from your browser into the config file of this project.


The transcriptor utilizes GPU Acceleration to function at full capacity. If you do not have a CUDA capable GPU or would like to process on your CPU, set FP16 to "False" in the config file. It is recommended to also consider using a smaller model if using a CPU to transcript (See whisper github fro more info) 
 
 
