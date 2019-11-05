package com.debiao.chatbot;

public class WeChatConfig {
	// Mini program
	protected static final String Program_Id = "wxeXXXXXXX";
	protected static final String Program_Key = "XXXXXXXXXX";

	// Wechat API
	protected static final String API_Code2Session = "https://api.weixin.qq.com/sns/jscode2session";
	
    // AppID
	public static final String APP_ID = "wxaXXXXXX";

	// Connection to backend server
	public static final String sai_url = "http://XXXXX/ask";

	// Connection to iFlyTek
    public static final String APPID = "appid=XXXXXXX";  
    protected static final String languageChinese = "zh_cn";
    
    // For audio processing
    private static final String driver = "D";
    public static final String folderUserInfo = driver + ":\\SAI\\UserInfos";
    public static final String folderInbound = "Inbound";
    public static final String audioToolPath = "C:\\ffmpeg\\bin\\ffmpeg.exe";
}
