// This script should be injected into the page (content.js)
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  console.log("Got Event")
  if (request.action === 'getActiveImage') {
    console.log("Got getActiveImage")
    let src = window.location.href

    // Try get WX_ACTIVEIMAGE class
    try {

      const wx_active = document.getElementsByClassName("WX_ACTIVEIMAGE")
      if (wx_active) {
        const imgElement = wx_active[0].querySelector('img'); // Adjust the selector as needed
        src = imgElement ? imgElement.src : window.location.href; // Retrieve the src attribute
      }
    } catch (e) {
      console.error(e)
    }

    console.log("Got src: " + src)
    // Send the src back to the popup
    sendResponse({ src });
    return true;
  }
});
