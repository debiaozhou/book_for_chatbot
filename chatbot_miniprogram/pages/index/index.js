// index.js v1.0.0
// Copyright 2019, Debiao Zhou
// 调用中台服务的接口
const sendMessageService = require('../../config').sendMessageServiceUrl
const sendAudioServiceUrl = require('../../config').sendAudioServiceUrl
// 录音管理器
const recorderManager = wx.getRecorderManager()
// 录音参数
const options = {
  duration: 7000,
  sampleRate: 44100,
  numberOfChannels: 1,
  encodeBitRate: 192000,
  format: 'mp3'
}
// 页面变量
var transcript = ''
var script = ''
var thisPage = null
var userID = ''
var sessionID = ''
var isRecording = false

Page({
  data: {
    transcript: '',
    script: ''
  },
  inputScript: function (e) {
    // 保存输入框中的输入
    console.log(e)
    script = e.detail.value
  },
  sendMessage: function (e) {
    // 发送消息
    console.log('发送消息')
    transcript = transcript + '\n我：' + script
    thisPage.setData({
      transcript: transcript,
      script: ''
    })
    // 调用中台接口
    wx.getStorage({
      key: 'sessionID',
      success: function (res) {
        console.log(res.data)
        if (res.data) {
          //发起网络请求
          wx.request({
            url: sendMessageService,
            data: {
              method: 'sendMessage',
              sessionID: res.data,
              script: script
            },
            method: 'POST',
            header: {
              'content-type': 'application/json' // 默认值
            },
            success: function (res) {
              console.log(res.data)
              transcript = transcript + '\n机器人：' + res.data.text
              thisPage.setData({
                transcript: transcript,
                script: ''
              })
            },
            fail: function (res) {
              console.log(res)
              transcript = transcript + '\n我：消息发送失败。'
              thisPage.setData({
                transcript: transcript,
                script: ''
              })
            }
          })
        }
      }
    })
  },
  recordMessage: function (e) {
    if (!isRecording) {
      // 开始录音
      console.log('开始录音')
      recorderManager.start(options)
      isRecording = true
    }
    else {
      // 结束录音
      console.log('结束录音')
      recorderManager.stop()
      isRecording = false
    }
  },
  onLoad: function () {
    // 初始化
    this.setData({
      transcript: '',
      script: ''
    })
    thisPage = this
    // 取得用户ID
    wx.getStorage({
      key: 'userID',
      success: function (e) {
        console.log('userID', e.data)
        userID = e.data
      }
    })
    // 取得sessionID
    wx.getStorage({
      key: 'sessionID',
      success: function (e) {
        console.log('sessionID', e.data)
        sessionID = e.data
      }
    })
  }
})
recorderManager.onStop((res) => {
  // 录音结束
  console.log('录音结束', res)
  // 上传录音文件
  uploadFile(res.tempFilePath)
})
function uploadFile(filePath) {
  // 上传录音文件
  console.log('上传录音文件')
  wx.uploadFile({
    url: sendAudioServiceUrl,
    filePath: filePath,
    name: 'file',
    formData: { "userID": userID, "sessionID": sessionID },
    header: { 'content-type': 'multipart/form-data' },
    success: function (res) {
      console.log(res.data)
      var text = JSON.parse(res.data).text
      transcript = transcript + '\n机器人：' + text
      thisPage.setData({
        transcript: transcript,
        script: ''
      })
    },
    fail: function (res) {
      console.log(res)
      transcript = transcript + '\n我：语音发送失败。'
      thisPage.setData({
        transcript: transcript,
        script: ''
      })
    }
  })
}
