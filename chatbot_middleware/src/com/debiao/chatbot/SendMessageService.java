package com.debiao.chatbot;

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.io.OutputStreamWriter;
import java.net.URL;

import javax.net.ssl.HttpsURLConnection;
import javax.servlet.ServletException;
import javax.servlet.annotation.WebServlet;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

import org.json.JSONObject;


@WebServlet("/SendMessageService")
public class SendMessageService extends HttpServlet {
	private static final long serialVersionUID = 1L;
    
    public SendMessageService() {
        super();
    }

    protected void doGet(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException {
    	// call doPost
    	doPost(request, response);
	}
	
    public void doPost(HttpServletRequest request, HttpServletResponse response)  
            throws ServletException, IOException {
    	// process request from mini program‚
    	
    	// ensure input and output are utf-8
        request.setCharacterEncoding("UTF-8");  
        response.setCharacterEncoding("UTF-8");  
  
        // receive input message
        StringBuffer sb = new StringBuffer();  
        InputStream is = request.getInputStream();  
        InputStreamReader isr = new InputStreamReader(is, "UTF-8");  
        BufferedReader br = new BufferedReader(isr);  
        String s = "";  
        while ((s = br.readLine()) != null) {  
            sb.append(s);  
        }  
        String requestString = sb.toString(); 
        JSONObject requestJason = new JSONObject(requestString);
        String result = "";  
        
        // process request from mini program
        String method = requestJason.getString("method");  
        if (method != null && ! method.isEmpty()) {  
            if (method.equals("login")) {
            	// login request
            	String code = requestJason.getString("code");
            	try {
            		// call wechat service
            		JSONObject input = new JSONObject();
        			input.put("appid", WeChatConfig.Program_Id);
        			input.put("secret", WeChatConfig.Program_Key);
        			input.put("js_code", code);
        			input.put("grant_type", "authorization_code");
            		String urlString = WeChatConfig.API_Code2Session + "?appid=" + WeChatConfig.Program_Id + "&secret=" + WeChatConfig.Program_Key + "&js_code=" + code + "&grant_type=authorization_code";
            		URL url = new URL(urlString);
          		  	HttpsURLConnection conn = (HttpsURLConnection) url.openConnection();
          		  	conn.setDoOutput(true);
          		  	conn.setRequestMethod("POST");
          		  	conn.setRequestProperty("Content-Type", "application/json");
          		  	conn.setRequestProperty("Accept", "application/json");
        			BufferedWriter bw = new BufferedWriter(new OutputStreamWriter(conn.getOutputStream(), "UTF-8"));
        			bw.write(input.toString());
        			bw.flush();
        			bw.close();
        			
        			// process message returned from wechat server
    				JSONObject jsonResultObj = new JSONObject();
        			if (conn.getResponseCode() == HttpsURLConnection.HTTP_OK) {
        				BufferedReader brResponse = new BufferedReader(new InputStreamReader((conn.getInputStream())));
        				String output = "";
        				String line = null;
        				while ((line = brResponse.readLine()) != null) {
        					output = output + line;
        				}
        				JSONObject jsonResult = new JSONObject(output);
        				if (jsonResult.has("session_key")) {
        					String sessionID = (String) jsonResult.get("session_key");
        					jsonResultObj.put("sessionID", sessionID);
        					result = jsonResultObj.toString();
        				}
        			}
        			else {
        				// error
        				jsonResultObj.put("errcode", "-1");
        				jsonResultObj.put("errmsg", "Https connection failed");
        				result = jsonResultObj.toString();
        			}
        			conn.disconnect();
            	} catch (Exception e) {
            		e.printStackTrace();
            	}
            }
	        else if (method.equals("sendMessage")) {
	        	// process dialog in text
	        	String script = requestJason.getString("script");
	        	String sessionID = requestJason.getString("sessionID");
	        	JSONObject jsonResult = new JSONObject();
	            String answer = new ChatbotProcess().getChatbotResult(sessionID, script);
	        	jsonResult.put("text", answer);
				result = jsonResult.toString();
	        }
        }

        // return message to mini program
        try {  
            OutputStream os = response.getOutputStream();  
            os.write(result.getBytes("UTF-8"));  
            os.flush();  
            os.close();  
        } catch (Exception e) {  
            e.printStackTrace();  
        }  
    }  
}
