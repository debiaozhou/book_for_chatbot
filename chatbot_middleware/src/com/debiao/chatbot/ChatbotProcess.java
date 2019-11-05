package com.debiao.chatbot;

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.InputStreamReader;
import java.io.OutputStreamWriter;
import java.net.HttpURLConnection;
import java.net.URL;

import org.json.JSONObject;

public class ChatbotProcess {
    public String getChatbotResult(String sessionID, String content){
    	// Call SAI
    	String result = "";
    	try {
    		URL url = new URL(WeChatConfig.sai_url);
  		  	HttpURLConnection conn = (HttpURLConnection) url.openConnection();
  		  	conn.setDoOutput(true);
  		  	conn.setRequestMethod("POST");
  		  	conn.setRequestProperty("Content-Type", "application/json");
  		  	conn.setRequestProperty("Accept", "application/json");

  		  	// Fill input parameter
			JSONObject input = new JSONObject();
			input.put("sessionID", sessionID);
			input.put("content", content);
			BufferedWriter bw = new BufferedWriter(new OutputStreamWriter(conn.getOutputStream(), "UTF-8"));
			bw.write(input.toString());
			bw.flush();
			bw.close();
			
			if (conn.getResponseCode() == HttpURLConnection.HTTP_OK) {
				BufferedReader br = new BufferedReader(new InputStreamReader((conn.getInputStream())));
				String output = "";
				String line = null;
				while ((line = br.readLine()) != null) {
					output = output + line;
				}
				JSONObject resultJson = new JSONObject(output);
				result = (String) resultJson.get("content");
			}
			conn.disconnect();
    	} catch (Exception e) {
    		e.printStackTrace();
    	}
  	  
        return result;  
    }  
}
