// Content script for safe webpage context extraction
// Only runs when the user explicitly enables webpage context in the popup

(() => {
  chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === "extract_page_context") {
      try {
        const title = document.title || "";
        const url = window.location.href || "";
        const selection = window.getSelection() ? window.getSelection().toString().trim() : "";

        sendResponse({
          success: true,
          page_title: title,
          page_url: url,
          selected_text: selection.slice(0, 1000) // limit safe length
        });
      } catch (err) {
        sendResponse({
          success: false,
          error: err.message
        });
      }
    }
    return true;
  });
})();
