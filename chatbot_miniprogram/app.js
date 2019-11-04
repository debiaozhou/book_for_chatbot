/**
 * app.js v1.0.0
 * Copyright 2019, Debiao Zhou
 */
const sendMessageServiceUrl = require('./config').sendMessageServiceUrl
App({
  onLaunch: function () {
    console.log('启动App')
    wx.login({
      success: function (res) {
        if (res.code) {
          //发起网络请求
          wx.request({
            url: sendMessageServiceUrl,
            data: {
              method: 'login',
              code: res.code
            },
            method: 'POST',
            header: {
              'content-type': 'application/json' // 默认值
            },
            success: function (res) {
              wx.setStorage({
                key: "sessionID",
                data: res.data.sessionID
              })
              wx.setStorage({
                key: "userID",
                data: res.data.userID
              })
            }
          })
        } else {
          console.log('登录失败！' + res.errMsg)
        }
      }
    });
  }
})