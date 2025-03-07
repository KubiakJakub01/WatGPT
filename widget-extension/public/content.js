(async function injectWidget() {
  try {
    const script = document.createElement("script");
    // eslint-disable-next-line no-undef
    script.src = chrome.runtime.getURL("widget.js");
    script.type = "module";
    script.onload = function () {
      this.remove();
    };
    (document.head || document.documentElement).appendChild(script);
    console.log("[Chat Widget] Injected!");
  } catch (error) {
    console.error("[Chat Widget] Injection failed:", error);
  }
})();
