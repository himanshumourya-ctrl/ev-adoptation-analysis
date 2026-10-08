(function () {
  function sendMessage(type, payload) {
    if (window.parent && window.parent.postMessage) {
      window.parent.postMessage({ type: type, ...(payload || {}) }, '*');
    }
  }

  const Streamlit = {
    RENDER_EVENT: 'streamlit:render',
    events: {
      addEventListener: function (eventName, callback) {
        window.addEventListener('message', function (event) {
          if (event.data && event.data.type === eventName) {
            callback(event.data);
          }
        });
      },
    },
    setComponentReady: function () {
      sendMessage('streamlit:componentReady', { apiVersion: 1 });
    },
    setComponentValue: function (value) {
      sendMessage('streamlit:setComponentValue', { value: value });
    },
    setFrameHeight: function (height) {
      sendMessage('streamlit:setFrameHeight', { height: height });
    },
  };

  window.Streamlit = Streamlit;
})();
