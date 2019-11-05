package com.debiao.chatbot;

import java.io.File;
import java.io.FileInputStream;
import java.io.IOException;
import java.util.ArrayList;

import com.iflytek.cloud.speech.RecognizerListener;
import com.iflytek.cloud.speech.RecognizerResult;
import com.iflytek.cloud.speech.Setting;
import com.iflytek.cloud.speech.SpeechConstant;
import com.iflytek.cloud.speech.SpeechError;
import com.iflytek.cloud.speech.SpeechRecognizer;
import com.iflytek.cloud.speech.SpeechSynthesizer;
import com.iflytek.cloud.speech.SpeechUtility;
import com.iflytek.cloud.speech.SynthesizeToUriListener;

public class VoiceTextTransformer {
    private StringBuffer mResult = new StringBuffer(); 
      
    // wait time
    private int perWaitTime = 100;  
    // repeat times when error  
    private int maxQueueTimes = 3;  
    // audio file
    private String fileName = ""; 
    // language
    private String language = "zh_cn";
    
    static {  
        Setting.setShowLog(false);  
        SpeechUtility.createUtility(WeChatConfig.APPID);  
    }  
      
    public String transform(String fileName, String language, boolean init) throws InterruptedException {  
    	// convert voice to text
    	
    	this.fileName = fileName;
        this.language = language;
        if(init) {  
            maxQueueTimes = 3;  
        }  
        if(maxQueueTimes <= 0) {  
            mResult.setLength(0);  
            mResult.append("processing error");  
            return mResult.toString();  
        }  
          
        return recognize();  
    }  
  
    private String recognize() throws InterruptedException {  
        if (SpeechRecognizer.getRecognizer() == null)  
            SpeechRecognizer.createRecognizer();  
        return RecognizeWavfileByte();  
    }  
  
    public RecognizerListener recListener = new RecognizerListener() {  
    	  
        public void onBeginOfSpeech() {
        }  
  
        public void onEndOfSpeech() {
        }  
  
        public void onVolumeChanged(int volume) { }  
  
        public void onResult(RecognizerResult result, boolean islast) {  
            mResult.append(result.getResultString());  
        }  

        public void onError(SpeechError error) {  
        }  
  
        public void onEvent(int eventType, int arg1, int agr2, String msg) {
        }  
  
    };

    private String RecognizeWavfileByte() throws InterruptedException { 
    	// recognize voice
    	        
        // 1. read audio file
        FileInputStream fis = null;  
        byte[] voiceBuffer = null;  
        try {  
            fis = new FileInputStream(new File(fileName));  
            voiceBuffer = new byte[fis.available()];  
            fis.read(voiceBuffer);  
        } catch (Exception e) {  
            e.printStackTrace();  
        } finally {  
            try {  
                if (null != fis) {  
                    fis.close();  
                    fis = null;  
                }  
            } catch (IOException e) {  
                e.printStackTrace();  
            }  
        }  
        
        // 2. listen to audio stream
        if (voiceBuffer == null || 0 == voiceBuffer.length) {  
        	// Error  
        } else {  
            mResult.setLength(0);  
            SpeechRecognizer recognizer = SpeechRecognizer.getRecognizer();  
            recognizer.setParameter(SpeechConstant.DOMAIN, "iat");  
            recognizer.setParameter(SpeechConstant.LANGUAGE, this.language);  
            if (this.language.equals(WeChatConfig.languageChinese)) {
                recognizer.setParameter(SpeechConstant.ACCENT, "mandarin");              	
            }
            recognizer.setParameter(SpeechConstant.AUDIO_SOURCE, "-1");  
            recognizer.setParameter( SpeechConstant.RESULT_TYPE, "plain" );  
            recognizer.startListening(recListener);  
            ArrayList<byte[]> buffers = splitBuffer(voiceBuffer,  
                    voiceBuffer.length, 4800);  
            for (int i = 0; i < buffers.size(); i++) {  
                recognizer.writeAudio(buffers.get(i), 0, buffers.get(i).length);  
                try {  
                    Thread.sleep(150);  
                } catch (InterruptedException e) {  
                    e.printStackTrace();  
                }  
            }  
            recognizer.stopListening();  
              
            while(recognizer.isListening()) {  
            	Thread.sleep(perWaitTime);  
            }  
        }  
        return mResult.toString();  
    }  
  
    private ArrayList<byte[]> splitBuffer(byte[] buffer, int length, int spsize) {  
        ArrayList<byte[]> array = new ArrayList<byte[]>();  
        if (spsize <= 0 || length <= 0 || buffer == null  
                || buffer.length < length)  
            return array;  
        int size = 0;  
        while (size < length) {  
            int left = length - size;  
            if (spsize < left) {  
                byte[] sdata = new byte[spsize];  
                System.arraycopy(buffer, size, sdata, 0, spsize);  
                array.add(sdata);  
                size += spsize;  
            } else {  
                byte[] sdata = new byte[left];  
                System.arraycopy(buffer, size, sdata, 0, left);  
                array.add(sdata);  
                size += left;  
            }  
        }  
        return array;  
    }  
}
