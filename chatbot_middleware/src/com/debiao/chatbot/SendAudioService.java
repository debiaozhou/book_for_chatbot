package com.debiao.chatbot;

import java.io.BufferedOutputStream;
import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.util.List;

import javax.servlet.ServletException;
import javax.servlet.annotation.WebServlet;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

import org.apache.commons.fileupload.FileItem;
import org.apache.commons.fileupload.disk.DiskFileItemFactory;
import org.apache.commons.fileupload.servlet.ServletFileUpload;
import org.json.JSONObject;


@WebServlet("/SendAudioService")
public class SendAudioService extends HttpServlet {
	private static final long serialVersionUID = 1L;
    
    public SendAudioService() {
        super();
    }

    protected void doGet(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException {
		// call doPost
    	
    	doPost(request, response);
	}
	
    public void doPost(HttpServletRequest request, HttpServletResponse response)  
            throws ServletException, IOException {
    	// process audio information from mini program
    	
    	String result = "";
    	
    	try {
    	    // save audio file under temporary folder
    		DiskFileItemFactory factory = new DiskFileItemFactory();
    		File dir = new File("c:\\temp");
    	    factory.setRepository(dir);
            // set buffer size
            factory.setSizeThreshold(1024 * 1024);
    		ServletFileUpload upload = new ServletFileUpload(factory);
	    	List<FileItem> list = upload.parseRequest(request);
	    	JSONObject jsonRequest = new JSONObject();
	    	FileItem uploadFile = null;
	        for(FileItem item : list){
	            // get field name
	            String name = item.getFieldName();
	            if(item.isFormField()){
	                String value = item.getString() ;
	                jsonRequest.put(name, value);
	            }
	            else {
	            	uploadFile = item;
	            }
	        }
	        String sessionID = jsonRequest.getString("sessionID");
            String filePath = WeChatConfig.folderUserInfo + "\\" + sessionID + "\\" + WeChatConfig.folderInbound; 
            dir = new File(filePath);  
            if (! dir.exists()) {  
                dir.mkdirs();  
            }  
            if (! filePath.endsWith("\\")) {  
            	filePath += "\\";  
            }  
    	    InputStream filecontent = uploadFile.getInputStream();
	    	String fileSavePath = filePath + "audio.mp3";
	        BufferedOutputStream out = new BufferedOutputStream(new FileOutputStream(fileSavePath));  

	        int read = 0;
	        final byte[] bytes = new byte[1048576];

	        while ((read = filecontent.read(bytes)) != -1) {
	            out.write(bytes, 0, read);
	        }
	        if (filecontent != null) {
	        	filecontent.close();
	        }
	        if (out != null) {
	            out.close();
	        }
	        
	        // convert mp3 to wav, and call external service to tranform into text
			try {
	        	JSONObject jsonResult = new JSONObject();
				String answer = ProcessAudioFile(sessionID, this, fileSavePath, jsonRequest);
	        	jsonResult.put("text", answer);
				result = jsonResult.toString();

			} catch (InterruptedException e) {
				e.printStackTrace();
			} 
	    } catch (Exception e) {  
	        e.printStackTrace();  
	    }  
    	
        try {  
            OutputStream os = response.getOutputStream();  
            os.write(result.getBytes("UTF-8"));  
            os.flush();  
            os.close();  
        } catch (Exception e) {  
            e.printStackTrace();  
        }  
    }

     private String ProcessAudioFile(String sessionID, SendAudioService wechatProcess, String fileSavePath, JSONObject parameters) throws InterruptedException {  
        // process audio dialog
    	
    	// convert mp3 to wav
        String newFileName = fileSavePath + ".wav";
        Mp3ChangeToWavByFfmpegTool(fileSavePath, newFileName);
        
        // process wav file
        String result = "";
		try {
			// convert audio to text
			VoiceTextTransformer mObject = new VoiceTextTransformer();  
			result = mObject.transform(newFileName, "zh_cn", true);
			
			// call backend service to process dialog
        	JSONObject jsonResult = new JSONObject();
            String answer = new ChatbotProcess().getChatbotResult(sessionID, result);
        	jsonResult.put("text", answer);
			result = jsonResult.toString();			
		} catch (InterruptedException e) {
			e.printStackTrace();
		}   
        
        return result;  
    }
    
    public void Mp3ChangeToWavByFfmpegTool(String sourcePath,String targetPath){
	  // convert audio file format

    	File tool = new File(WeChatConfig.audioToolPath);
    	if (tool.exists()) {
    		String c = "\"" + WeChatConfig.audioToolPath + "\"" + " -y -i " + "\"" + sourcePath + "\"" + " -ar 16000 -ab 16 -ac 1 " + "\"" + targetPath + "\"";
    		try {
    			Process p = Runtime.getRuntime().exec(c);
    			p.waitFor();
    			p.destroy();
    		} catch (IOException e) {
    			e.printStackTrace();
    		} catch (InterruptedException e) {
    			e.printStackTrace();
    		}
    	}else {
    		System.out.println("ffmpeg doesn't exist");
    	}
    }
}
