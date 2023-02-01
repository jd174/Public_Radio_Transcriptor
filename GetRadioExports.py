import time
import datetime
import requests
from pathlib import Path
import pickle
import os
import speech_recognition as sr
from pydub import AudioSegment
import whisper
import TrimAudio
import json
import pandas as pd
import re
import configparser
import logging
import sys


now = datetime.datetime.now()
CurrentDate=now.strftime("%m/%d/%Y")
CurrentTimestamp = str(int(time.time()*1000))


def parseChunks(Chunks,Directory,Broadcast):
    Transcript={}
    AllData=[]
    model = whisper.load_model(str(config.get('DEFAULT','WhisperModel')))
    print("\nparsing...")
    for x in Chunks:
        srcfile=(os.path.join(Directory,"Chunks",x))
        result = model.transcribe(srcfile)
        Transcript[x]=result['text']
        AllData.append(result)
    with open(os.path.join(Directory,Broadcast+".json"), "w") as outfile:
        json.dump(Transcript, outfile)
    with open(os.path.join(Directory,Broadcast+"_AllData.json"), "w") as outfile:
        json.dump(AllData, outfile)
    print("\nDone")

def ParseClip(Clip,Directory,Broadcast):
    Transcript={}
    AllData=[]
    model = whisper.load_model(str(config.get('DEFAULT','WhisperModel')))
    print("\nparsing...")
    srcfile=Clip
    result = model.transcribe(srcfile)
    Transcript=result['text']
    AllData.append(result)
    with open(os.path.join(Directory,Broadcast+".json"), "w") as outfile:
        json.dump(Transcript, outfile)
    with open(os.path.join(Directory,Broadcast+"_AllData.json"), "w") as outfile:
        json.dump(AllData, outfile)
    print("\nDone")

def GetLatestBroadcast(Directory):

    with open(os.path.join(Directory,"Broadcasts","BroadcastList.pkl"), 'rb') as f:
        BroadcastList = pickle.load(f)
    f.close()

    BaseURL="https://m.broadcastify.com/archives/ajax.php?feedId="
    url=BaseURL+feedid+"&date="+CurrentDate+"&_="+CurrentTimestamp
    response=requests.get(url)
    LatestBroadcast=response.json()['data'][0]

    if str(LatestBroadcast[0]) not in BroadcastList:
        return(LatestBroadcast[0])
    else:
        return("")


        

def DownloadMP3(LatestBroadcast,Directory):
    try:
        BaseURL="https://m.broadcastify.com/archives/downloadv2/"

        response=requests.get(url=BaseURL+LatestBroadcast,cookies=cookies)
        mp3URL=str(response.url)

        MP3 = requests.get(mp3URL)
        Path(os.path.join(Directory,"Broadcasts",LatestBroadcast)).mkdir(parents=True, exist_ok=True)
        with open(os.path.join(Directory,"Broadcasts",LatestBroadcast,LatestBroadcast+".mp3"), 'wb') as f:
            f.write(MP3.content)

        with open(os.path.join(Directory,"Broadcasts","BroadcastList.pkl"), 'rb') as f:
            BroadcastList = pickle.load(f)
        f.close()
        BroadcastList.append(LatestBroadcast)
        print(BroadcastList)
        with open(os.path.join(Directory,"Broadcasts","BroadcastList.pkl"), 'wb') as f:
            pickle.dump(BroadcastList, f)
        f.close()     
    except:
        print()


def CreateCSV(Broadcast):
    with open(Path(os.path.join(os.path.dirname(os.path.realpath(__file__)),"FeedArchives",now.strftime("%m.%d.%Y"),"Broadcasts",Broadcast,Broadcast+"_AllData.json"))) as f:
        data = json.loads(f.read())
        timestamp=re.findall("(?<=\-).*",Broadcast)[0]
        Date = datetime.datetime.fromtimestamp(int(timestamp))
        df=pd.DataFrame.from_dict(data[0]['segments'])
        df['DateTime']=Date
        df['DateTime']=pd.to_datetime(df['DateTime'])
        df=df.sort_values(by=['DateTime','id'],ascending=True)
        df.to_csv(Path(os.path.join(os.path.dirname(os.path.realpath(__file__)),"FeedArchives",now.strftime("%m.%d.%Y"),"Broadcasts",Broadcast,"Transcipt.csv")))

def main():
    
    TodayArchiveDirectory=os.path.join(os.path.dirname(os.path.realpath(__file__)),"FeedArchives",now.strftime("%m.%d.%Y"))
    #Make Directories if they don't exist
    logging.info("Creating necessary Directories")
    Path(TodayArchiveDirectory).mkdir(parents=True, exist_ok=True)
    Path(os.path.join(TodayArchiveDirectory,"Broadcasts")).mkdir(parents=True, exist_ok=True)
    if not os.path.exists(os.path.join(TodayArchiveDirectory,"Broadcasts","BroadcastList.pkl")):
        with open(os.path.join(TodayArchiveDirectory,"Broadcasts","BroadcastList.pkl"), 'wb') as f:
            pickle.dump([], f)
        f.close()
    
    Broadcast=""
    while Broadcast=="":
        Broadcast=GetLatestBroadcast(TodayArchiveDirectory)
        if Broadcast=="":
            logging.info("Waiting for new Broadcast...")
            print("\nWaiting for new Broadcast...")
            time.sleep(300)

    logging.info("New Broadcast Identified!")
    print("\nNew Broadcast Identified!")
    logging.info("Downloading latest Broadcast...")
    DownloadMP3(Broadcast,TodayArchiveDirectory)
    logging.info("Done.")

    logging.info("Removing Silence from Broadcast...")
    TrimAudio.OneClipTrimmer(
        File= Path(os.path.join(TodayArchiveDirectory,"Broadcasts",Broadcast,Broadcast+".mp3")),
        directory= Path(os.path.join(TodayArchiveDirectory,"Broadcasts",Broadcast)))
    logging.info("Done.")

    logging.info("Parsing Audio clip...")
    ParseClip(
        Clip=os.path.join(TodayArchiveDirectory,"Broadcasts",Broadcast,"VoicesNoSilence.mp3"),
        Directory=Path(os.path.join(TodayArchiveDirectory,"Broadcasts",Broadcast)),
        Broadcast=Broadcast
    )
    logging.info("Done.")

    CreateCSV(Broadcast=Broadcast)

    #       CHUNKS
    # Path(os.path.join(TodayArchiveDirectory,"Broadcasts",Broadcast,"Chunks")).mkdir(parents=True, exist_ok=True)
    # TrimAudio.SilenceTrimmer(
    #     File= Path(os.path.join(TodayArchiveDirectory,"Broadcasts",Broadcast,Broadcast+".mp3")),
    #     directory= Path(os.path.join(TodayArchiveDirectory,"Broadcasts",Broadcast,"Chunks")))
    # Chunks=os.listdir(Path(os.path.join(TodayArchiveDirectory,"Broadcasts",Broadcast,"Chunks")))
    # parseChunks(
    #     Chunks=Chunks,
    #     Directory=Path(os.path.join(TodayArchiveDirectory,"Broadcasts",Broadcast,"Chunks")),
    #     Broadcast=Broadcast)



Path('AppLogs').mkdir(parents=True,exist_ok=True)
logging.basicConfig(filename="AppLogs/Applogs_"+now.strftime("%m.%d.%Y")+".log", filemode='a',format="%(asctime)s - %(message)s",level="INFO")
logging.info("Starting application")
logging.info("Reading Configuration file")
try:
    logging.info("Reading Configuration file")
    config = configparser.RawConfigParser()
    ini_path = os.path.join(os.path.dirname(os.path.realpath(__file__)),'config.ini')
    config.read(ini_path)
except Exception as e:
    logging.info("There was an error reading the conifguration file.")
    logging.info(str(e))
    sys.exit()

cookies = {
    '_ga': config.get('DEFAULT','_ga'),
    '_gid': config.get('DEFAULT','_gid'),
    '__gads': config.get('DEFAULT','__gads'),
    '__gpi': config.get('DEFAULT','__gpi'),
    'bcfyuser1': config.get('DEFAULT','bcfyuser1'),
    '_awl': config.get('DEFAULT','_awl'),
}

feedid = str(config.get('DEFAULT','RadioToWatch'))

while True:
    main()