// YouTube 字幕翻译 - Background Service Worker

chrome.runtime.onInstalled.addListener(() => {
  console.log('YouTube 字幕翻译扩展已安装');
  
  // 设置默认配置
  chrome.storage.sync.set({
    enabled: true,
    targetLang: 'vi',
    ttsEnabled: true
  });
});

chrome.runtime.onStartup.addListener(() => {
  chrome.storage.sync.set({targetLang: 'vi', ttsEnabled: true});
});

// 监听来自 content script 的消息
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'gemini_tts') {
    fetch('http://127.0.0.1:8765/tts', {
      method: 'POST', headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({text: request.text})
    }).then(async response => {
      if (!response.ok) throw new Error(`TTS endpoint HTTP ${response.status}`);
      const bytes = Array.from(new Uint8Array(await response.arrayBuffer()));
      sendResponse({success: true, bytes});
    }).catch(error => sendResponse({success: false, error: error.message}));
    return true;
  }
  if (request.action === 'translate') {
    // 可以在这里添加更复杂的翻译逻辑
    // 比如使用付费 API、本地模型等
    sendResponse({ success: true });
  }
  return true;
});
