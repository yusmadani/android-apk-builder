#!/usr/bin/env python3
"""
Universal Native Shell (Dual Input: CLI Args + Payload JSON)
- Mengunci Gradle Wrapper ke versi 8.7 (Kompatibel penuh dengan AGP 8.5.2).
- Menggunakan AndroidX WebViewAssetLoader (HTTPS Domain Resmi).
- Built-in Pro Mobile UI Kit (Glassmorphism & Haptic) 100% Offline.
"""
import base64
import json
import os
import pathlib
import re
import sys

ROOT = pathlib.Path(".")
PAYLOAD = pathlib.Path("payload.json")

LT = chr(60)
GT = chr(62)

PRO_UI_CSS = """
:root {
  --bg-main: #0B0F19;
  --bg-card: #151D2E;
  --bg-card-hover: #1E293B;
  --border-color: #22304A;
  --accent-primary: #6366F1;
  --accent-gradient: linear-gradient(135deg, #6366F1 0%, #8B5CF6 100%);
  --accent-emerald: linear-gradient(135deg, #10B981 0%, #059669 100%);
  --text-main: #F8FAFC;
  --text-muted: #94A3B8;
  --danger: #EF4444;
  --safe-bottom: env(safe-area-inset-bottom, 20px);
}
* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
  -webkit-tap-highlight-color: transparent;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
  user-select: none;
}
body {
  background-color: var(--bg-main);
  color: var(--text-main);
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  overflow-x: hidden;
  padding-bottom: calc(75px + var(--safe-bottom));
}
.app-header {
  position: sticky;
  top: 0;
  z-index: 50;
  background: rgba(11, 15, 25, 0.85);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border-bottom: 1px solid var(--border-color);
  padding: 14px 18px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.app-header h1 {
  font-size: 1.15rem;
  font-weight: 700;
  letter-spacing: -0.02em;
  background: var(--accent-gradient);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}
.container {
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 14px;
  flex: 1;
}
.card {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 16px;
  padding: 16px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.25);
  transition: transform 0.15s ease;
}
.card:active { transform: scale(0.99); }
.stat-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}
.stat-box {
  background: rgba(34, 48, 74, 0.4);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 12px;
  text-align: center;
}
.stat-val { font-size: 1.5rem; font-weight: 800; color: #F8FAFC; }
.stat-lbl {
  font-size: 0.75rem;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-top: 2px;
}
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 12px 18px;
  border-radius: 12px;
  font-size: 0.92rem;
  font-weight: 600;
  border: none;
  cursor: pointer;
  background: var(--accent-gradient);
  color: #FFFFFF;
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.35);
  transition: all 0.15s ease;
  width: 100%;
}
.btn:active { transform: scale(0.97); opacity: 0.9; }
.btn-emerald { background: var(--accent-emerald); box-shadow: 0 4px 12px rgba(16, 185, 129, 0.35); }
.btn-danger { background: var(--danger); box-shadow: 0 4px 12px rgba(239, 68, 68, 0.35); }
.btn-secondary { background: var(--bg-card-hover); border: 1px solid var(--border-color); color: var(--text-main); }
.input-group { display: flex; flex-direction: column; gap: 6px; margin-bottom: 12px; }
.input-group label { font-size: 0.8rem; color: var(--text-muted); font-weight: 500; }
.input-field {
  background: #0B0F19;
  border: 1px solid var(--border-color);
  border-radius: 10px;
  padding: 12px;
  color: #FFFFFF;
  font-size: 0.95rem;
  outline: none;
}
.input-field:focus { border-color: var(--accent-primary); }
.item-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px;
  background: rgba(11, 15, 25, 0.5);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  margin-bottom: 8px;
  gap: 10px;
}
.item-row.done { opacity: 0.5; text-decoration: line-through; }
.tab-bar {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  height: calc(62px + var(--safe-bottom));
  padding-bottom: var(--safe-bottom);
  background: rgba(15, 23, 42, 0.92);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border-top: 1px solid var(--border-color);
  display: flex;
  align-items: center;
  justify-content: space-around;
  z-index: 100;
}
.tab-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: none;
  border: none;
  color: var(--text-muted);
  font-size: 0.72rem;
  font-weight: 500;
  gap: 4px;
  cursor: pointer;
  flex: 1;
  height: 100%;
}
.tab-item.active { color: #A5B4FC; }
.tab-item .icon { font-size: 1.25rem; }
#debug-err-banner {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  background: #DC2626;
  color: white;
  padding: 10px;
  font-size: 11px;
  z-index: 999999;
  display: none;
}
"""

PRO_UI_JS = """
window.onerror = function(msg, url, line) {
  var b = document.getElementById('debug-err-banner');
  if (b) {
    b.style.display = 'block';
    b.innerHTML += '⚠️ <b>JS Error:</b> ' + msg + ' (L:' + line + ')<br>';
  }
};
window.DB = {
  get: function(key, defaultVal) {
    try {
      var val = localStorage.getItem(key);
      return val ? JSON.parse(val) : defaultVal;
    } catch(e) { return defaultVal; }
  },
  set: function(key, val) {
    try {
      localStorage.setItem(key, JSON.stringify(val));
      return true;
    } catch(e) { return false; }
  }
};
window.Native = {
  toast: function(msg) {
    if (window.Android && window.Android.showToast) { window.Android.showToast(msg); }
  },
  vibrate: function(ms) {
    if (window.Android && window.Android.vibrate) { window.Android.vibrate(ms || 40); }
  }
};
document.addEventListener('DOMContentLoaded', function() {
  document.querySelectorAll('button, .card, .tab-item').forEach(function(el) {
    el.addEventListener('click', function() { Native.vibrate(25); });
  });
});
"""

def clean_html_code(raw_code):
    if not raw_code:
        return ""
    code = raw_code.strip()
    code = re.sub(r"^```(?:html|xml)?\s*", "", code, flags=re.IGNORECASE)
    code = re.sub(r"\s*```$", "", code)
    return code.strip()

def assemble_pro_html(user_html, app_title):
    user_html = clean_html_code(user_html)
    injected = f"{LT}style{GT}{PRO_UI_CSS}{LT}/style{GT}\n{LT}script{GT}{PRO_UI_JS}{LT}/script{GT}"

    if f"{LT}body" in user_html.lower():
        if f"{LT}head{GT}" in user_html:
            user_html = user_html.replace(f"{LT}head{GT}", f"{LT}head{GT}\n{injected}")
        else:
            user_html = injected + "\n" + user_html

        if "debug-err-banner" not in user_html:
            user_html = user_html.replace(f"{LT}body{GT}", f"{LT}body{GT}\n{LT}div id='debug-err-banner'{GT}{LT}/div{GT}")
        return user_html

    return f"""<!DOCTYPE html>
<html lang="id">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
  <title>{app_title}</title>
  <style>{PRO_UI_CSS}</style>
  <script>{PRO_UI_JS}</script>
</head>
<body>
  <div id="debug-err-banner"></div>
  <header class="app-header">
    <h1>{app_title}</h1>
    <span style="font-size:1.2rem;">⚡</span>
  </header>
  <div class="container">
    {user_html}
  </div>
</body>
</html>"""

def main():
    raw_name = "ProApp"
    b64 = None

    if len(sys.argv) >= 3:
        raw_name = sys.argv[1]
        b64 = sys.argv[2]
    elif PAYLOAD.exists():
        try:
            data = json.loads(PAYLOAD.read_text(encoding="utf-8"))
            raw_name = data.get("app_name", "ProApp")
            b64 = data.get("html_code_b64") or data.get("xml_code_b64") or data.get("code_b64")
        except Exception as e:
            print(f"[WARN] Gagal membaca payload.json: {e}")

    clean_app_name = re.sub(r"[^\w\s-]", "", raw_name).strip() or "ProApp"
    pkg_suffix = re.sub(r"[^a-zA-Z0-9]", "", clean_app_name).lower() or "proapp"
    pkg = f"com.stb.{pkg_suffix}"

    if b64:
        try:
            raw_html = base64.b64decode(b64).decode("utf-8", errors="ignore")
        except Exception:
            raw_html = f"<div class='card'><h2>{clean_app_name}</h2><p>Gagal mendecode HTML payload.</p></div>"
    else:
        raw_html = f"<div class='card'><h2>{clean_app_name} Siap!</h2></div>"

    final_html = assemble_pro_html(raw_html, clean_app_name)

    def write(p, content):
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")

    # 1. Gradle Files & Gradle Wrapper 8.7 (Wajib untuk AGP 8.5.2)
    write(
        ROOT / "gradle" / "wrapper" / "gradle-wrapper.properties",
        (
            "distributionBase=GRADLE_USER_HOME\n"
            "distributionPath=wrapper/dists\n"
            "distributionUrl=https\\://services.gradle.org/distributions/gradle-8.7-bin.zip\n"
            "zipStoreBase=GRADLE_USER_HOME\n"
            "zipStorePath=wrapper/dists\n"
        ),
    )

    write(
        ROOT / "settings.gradle",
        (
            "pluginManagement { repositories { google(); mavenCentral(); gradlePluginPortal() } }\n"
            "dependencyResolutionManagement { repositoriesMode.set(RepositoriesMode.PREFER_SETTINGS); repositories { google(); mavenCentral() } }\n"
            f"rootProject.name = '{pkg_suffix}'\n"
            "include ':app'\n"
        ),
    )

    write(
        ROOT / "build.gradle",
        "plugins { id 'com.android.application' version '8.5.2' apply false }\n",
    )

    write(
        ROOT / "gradle.properties",
        (
            "org.gradle.jvmargs=-Xmx2048m -Dfile.encoding=UTF-8\n"
            "android.useAndroidX=true\n"
            "android.nonTransitiveRClass=true\n"
        ),
    )

    write(
        ROOT / "app" / "build.gradle",
        (
            "plugins { id 'com.android.application' }\n\n"
            "android {\n"
            f"    namespace '{pkg}'\n"
            "    compileSdk 34\n\n"
            "    defaultConfig {\n"
            f"        applicationId '{pkg}'\n"
            "        minSdk 21\n"
            "        targetSdk 34\n"
            "        versionCode 1\n"
            "        versionName '1.0'\n"
            "    }\n"
            "    buildTypes { release { minifyEnabled false } }\n"
            "    compileOptions {\n"
            "        sourceCompatibility JavaVersion.VERSION_17\n"
            "        targetCompatibility JavaVersion.VERSION_17\n"
            "    }\n"
            "}\n"
            "dependencies {\n"
            "    implementation 'androidx.webkit:webkit:1.10.0'\n"
            "}\n"
        ),
    )

    # 2. Android Manifest
    write(
        ROOT / "app" / "src" / "main" / "AndroidManifest.xml",
        (
            f"{LT}?xml version=\"1.0\" encoding=\"utf-8\"?{GT}\n"
            f"{LT}manifest xmlns:android=\"http://schemas.android.com/apk/res/android\"{GT}\n"
            f'    {LT}uses-permission android:name="android.permission.INTERNET" /{GT}\n'
            f'    {LT}uses-permission android:name="android.permission.ACCESS_NETWORK_STATE" /{GT}\n'
            f'    {LT}uses-permission android:name="android.permission.VIBRATE" /{GT}\n'
            f"    {LT}application\n"
            f'        android:allowBackup="true"\n'
            f'        android:icon="@drawable/ic_launcher"\n'
            f'        android:label="@string/app_name"\n'
            f'        android:hardwareAccelerated="true"\n'
            f'        android:theme="@android:style/Theme.DeviceDefault.NoActionBar"{GT}\n'
            f"        {LT}activity\n"
            f'            android:name=".MainActivity"\n'
            f'            android:configChanges="orientation|screenSize|keyboardHidden"\n'
            f'            android:exported="true"{GT}\n'
            f"            {LT}intent-filter{GT}\n"
            f'                {LT}action android:name="android.intent.action.MAIN" /{GT}\n'
            f'                {LT}category android:name="android.intent.category.LAUNCHER" /{GT}\n'
            f"            {LT}/intent-filter{GT}\n"
            f"        {LT}/activity{GT}\n"
            f"    {LT}/application{GT}\n"
            f"{LT}/manifest{GT}\n"
        ),
    )

    # 3. Resources
    write(
        ROOT / "app" / "src" / "main" / "res" / "values" / "strings.xml",
        f'{LT}resources{GT}{LT}string name="app_name"{GT}{clean_app_name}{LT}/string{GT}{LT}/resources{GT}',
    )
    write(
        ROOT / "app" / "src" / "main" / "res" / "drawable" / "ic_launcher.xml",
        (
            f"{LT}?xml version=\"1.0\" encoding=\"utf-8\"?{GT}\n"
            f'{LT}vector xmlns:android="http://schemas.android.com/apk/res/android" android:width="108dp" android:height="108dp" android:viewportWidth="108" android:viewportHeight="108"{GT}\n'
            f'    {LT}path android:fillColor="#0B0F19" android:pathData="M0,0h108v108h-108z"/{GT}\n'
            f'    {LT}path android:fillColor="#6366F1" android:pathData="M54,20L74,40H60V74H48V40H34L54,20Z"/{GT}\n'
            f"{LT}/vector{GT}\n"
        ),
    )

    # 4. Aset HTML
    write(ROOT / "app" / "src" / "main" / "assets" / "index.html", final_html)

    # 5. MainActivity
    java_code = (
        f"package {pkg};\n\n"
        "import android.annotation.SuppressLint;\n"
        "import android.app.Activity;\n"
        "import android.content.Context;\n"
        "import android.graphics.Color;\n"
        "import android.os.Build;\n"
        "import android.os.Bundle;\n"
        "import android.os.Vibrator;\n"
        "import android.view.Window;\n"
        "import android.view.WindowManager;\n"
        "import android.webkit.JavascriptInterface;\n"
        "import android.webkit.WebChromeClient;\n"
        "import android.webkit.WebResourceRequest;\n"
        "import android.webkit.WebResourceResponse;\n"
        "import android.webkit.WebSettings;\n"
        "import android.webkit.WebView;\n"
        "import android.webkit.WebViewClient;\n"
        "import android.widget.Toast;\n"
        "import androidx.webkit.WebViewAssetLoader;\n\n"
        "public class MainActivity extends Activity {\n"
        "    private WebView webView;\n\n"
        "    @SuppressLint(\"SetJavaScriptEnabled\")\n"
        "    @Override\n"
        "    protected void onCreate(Bundle savedInstanceState) {\n"
        "        super.onCreate(savedInstanceState);\n\n"
        "        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.LOLLIPOP) {\n"
        "            Window window = getWindow();\n"
        "            window.addFlags(WindowManager.LayoutParams.FLAG_DRAWS_SYSTEM_BAR_BACKGROUNDS);\n"
        "            window.setStatusBarColor(Color.parseColor(\"#0B0F19\"));\n"
        "            window.setNavigationBarColor(Color.parseColor(\"#0B0F19\"));\n"
        "        }\n\n"
        "        webView = new WebView(this);\n"
        "        webView.setBackgroundColor(Color.parseColor(\"#0B0F19\"));\n"
        "        setContentView(webView);\n\n"
        "        WebSettings ws = webView.getSettings();\n"
        "        ws.setJavaScriptEnabled(true);\n"
        "        ws.setDomStorageEnabled(true);\n"
        "        ws.setDatabaseEnabled(true);\n"
        "        ws.setAllowFileAccess(false);\n"
        "        ws.setAllowContentAccess(false);\n"
        "        ws.setLoadWithOverviewMode(true);\n"
        "        ws.setUseWideViewPort(true);\n\n"
        "        final WebViewAssetLoader assetLoader = new WebViewAssetLoader.Builder()\n"
        "            .addPathHandler(\"/assets/\", new WebViewAssetLoader.AssetsPathHandler(this))\n"
        "            .build();\n\n"
        "        webView.setWebViewClient(new WebViewClient() {\n"
        "            @Override\n"
        "            public WebResourceResponse shouldInterceptRequest(WebView view, WebResourceRequest request) {\n"
        "                return assetLoader.shouldInterceptRequest(request.getUrl());\n"
        "            }\n"
        "        });\n\n"
        "        webView.setWebChromeClient(new WebChromeClient());\n"
        "        webView.addJavascriptInterface(new NativeBridge(this), \"Android\");\n\n"
        "        webView.loadUrl(\"https://appassets.androidplatform.net/assets/index.html\");\n"
        "    }\n\n"
        "    @Override\n"
        "    public void onBackPressed() {\n"
        "        if (webView != null && webView.canGoBack()) {\n"
        "            webView.goBack();\n"
        "        } else {\n"
        "            super.onBackPressed();\n"
        "        }\n"
        "    }\n\n"
        "    public class NativeBridge {\n"
        "        private final Context context;\n"
        "        NativeBridge(Context c) { this.context = c; }\n\n"
        "        @JavascriptInterface\n"
        "        public void showToast(final String message) {\n"
        "            runOnUiThread(new Runnable() {\n"
        "                @Override\n"
        "                public void run() {\n"
        "                    Toast.makeText(context, message, Toast.LENGTH_SHORT).show();\n"
        "                }\n"
        "            });\n"
        "        }\n\n"
        "        @JavascriptInterface\n"
        "        public void vibrate(final long ms) {\n"
        "            try {\n"
        "                Vibrator v = (Vibrator) context.getSystemService(Context.VIBRATOR_SERVICE);\n"
        "                if (v != null) v.vibrate(ms);\n"
        "            } catch (Exception ignored) {}\n"
        "        }\n"
        "    }\n"
        "}\n"
    )

    java_dir = ROOT / "app" / "src" / "main" / "java" / pathlib.Path(*pkg.split("."))
    write(java_dir / "MainActivity.java", java_code)
    print(f"[OK] Android Shell siap untuk {clean_app_name} ({pkg})")

if __name__ == "__main__":
    main()
