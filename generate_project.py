#!/usr/bin/env python3
"""
Universal Native Shell Generator (Auto-Fix LocalStorage & Anti-Blank)
- Menggunakan loadDataWithBaseURL (membuka kunci localStorage di Android).
- Injeksi otomatis Safe-Storage Polyfill & Visual JS Error Banner.
- Zero Javac / AAPT Error.
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


def clean_html(code):
    if not code:
        return ""
    code = code.strip()
    code = re.sub(r"^```(?:html|xml)?\s*", "", code, flags=re.IGNORECASE)
    code = re.sub(r"\s*```$", "", code)
    return code.strip()


def inject_safety_layer(html):
    """Menyuntikkan pelindung LocalStorage dan OnError Banner agar tidak pernah blank."""
    safety_script = f"""{LT}script{GT}
// 1. Tangkap error JS dan tampilkan banner merah di layar jika script bermasalah
window.onerror = function(msg, url, line) {{
    var b = document.getElementById('debug-err-banner');
    if (!b) {{
        b = document.createElement('div');
        b.id = 'debug-err-banner';
        b.style.cssText = 'position:fixed;top:0;left:0;right:0;background:#dc2626;color:#fff;padding:12px;z-index:999999;font-size:12px;font-family:sans-serif;box-shadow:0 4px 6px rgba(0,0,0,0.3);word-break:break-all;';
        if (document.body) {{ document.body.prepend(b); }}
        else {{ document.documentElement.appendChild(b); }}
    }}
    b.innerHTML += '⚠️ <b>JS Error:</b> ' + msg + ' (Baris: ' + line + ')<br>';
}};

// 2. Safe LocalStorage (Mencegah crash jika Android memblokir storage)
try {{
    var _testKey = '__storage_test__';
    window.localStorage.setItem(_testKey, _testKey);
    window.localStorage.removeItem(_testKey);
}} catch (e) {{
    console.warn('LocalStorage diblokir, mengaktifkan in-memory fallback');
    var _mem = {{}};
    window.localStorage = {{
        getItem: function(k) {{ return _mem.hasOwnProperty(k) ? _mem[k] : null; }},
        setItem: function(k, v) {{ _mem[k] = String(v); }},
        removeItem: function(k) {{ delete _mem[k]; }},
        clear: function() {{ _mem = {{}}; }}
    }};
}}
{LT}/script{GT}"""

    # Sisipkan tepat setelah tag <head> atau di paling atas dokumen
    if f"{LT}head{GT}" in html:
        return html.replace(f"{LT}head{GT}", f"{LT}head{GT}\n{safety_script}")
    elif f"{LT}html{GT}" in html:
        return html.replace(f"{LT}html{GT}", f"{LT}html{GT}\n{safety_script}")
    return safety_script + "\n" + html


def main():
    if not PAYLOAD.exists():
        sys.exit("[FATAL] payload.json tidak ada!")

    data = json.loads(PAYLOAD.read_text(encoding="utf-8"))
    raw_name = data.get("app_name", "DynamicApp")
    clean_app_name = re.sub(r"[^\w\s-]", "", raw_name).strip() or "DynamicApp"
    pkg_suffix = (
        re.sub(r"[^a-zA-Z0-9]", "", clean_app_name).lower() or "dynamicapp"
    )
    pkg = f"com.stb.{pkg_suffix}"

    # Baca HTML dari Base64
    b64 = (
        data.get("html_code_b64")
        or data.get("xml_code_b64")
        or data.get("code_b64")
    )
    if b64:
        raw_html = base64.b64decode(b64).decode("utf-8", errors="ignore")
        final_html = clean_html(raw_html)
    else:
        final_html = (
            f"<!DOCTYPE html>{LT}html{GT}{LT}head{GT}{LT}meta name='viewport' content='width=device-width, initial-scale=1.0'{GT}"
            f"{LT}style{GT}body{{background:#0f172a;color:#fff;font-family:sans-serif;display:flex;align-items:center;"
            f"justify-content:center;height:100vh;margin:0;}}{LT}/style{GT}{LT}/head{GT}"
            f"{LT}body{GT}{LT}h2{GT}{clean_app_name} Siap!{LT}/h2{GT}{LT}/body{GT}{LT}/html{GT}"
        )

    # Injeksi proteksi error & localStorage
    final_html = inject_safety_layer(final_html)

    def write(p, content):
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")

    # 1. Gradle Files
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
            "dependencies { implementation 'androidx.annotation:annotation:1.9.1' }\n"
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
            f'        android:usesCleartextTraffic="true"\n'
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
            f'    {LT}path android:fillColor="#0F172A" android:pathData="M0,0h108v108h-108z"/{GT}\n'
            f'    {LT}path android:fillColor="#10B981" android:pathData="M54,20L74,40H60V74H48V40H34L54,20Z"/{GT}\n'
            f"{LT}/vector{GT}\n"
        ),
    )

    # 4. Tulis file HTML ke Assets
    write(ROOT / "app" / "src" / "main" / "assets" / "index.html", final_html)

    # 5. MainActivity dengan loadDataWithBaseURL (Akses LocalStorage Resmi)
    java_code = (
        f"package {pkg};\n\n"
        "import android.app.Activity;\n"
        "import android.content.Context;\n"
        "import android.graphics.Color;\n"
        "import android.os.Build;\n"
        "import android.os.Bundle;\n"
        "import android.os.Vibrator;\n"
        "import android.webkit.JavascriptInterface;\n"
        "import android.webkit.WebChromeClient;\n"
        "import android.webkit.WebSettings;\n"
        "import android.webkit.WebView;\n"
        "import android.webkit.WebViewClient;\n"
        "import android.widget.Toast;\n"
        "import java.io.ByteArrayOutputStream;\n"
        "import java.io.InputStream;\n"
        "import java.nio.charset.StandardCharsets;\n\n"
        "public class MainActivity extends Activity {\n"
        "    private WebView webView;\n\n"
        "    @Override\n"
        "    protected void onCreate(Bundle savedInstanceState) {\n"
        "        super.onCreate(savedInstanceState);\n\n"
        "        webView = new WebView(this);\n"
        "        webView.setBackgroundColor(Color.parseColor(\"#0F172A\"));\n"
        "        setContentView(webView);\n\n"
        "        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.KITKAT) {\n"
        "            WebView.setWebContentsDebuggingEnabled(true);\n"
        "        }\n\n"
        "        WebSettings ws = webView.getSettings();\n"
        "        ws.setJavaScriptEnabled(true);\n"
        "        ws.setDomStorageEnabled(true);\n"
        "        ws.setDatabaseEnabled(true);\n"
        "        ws.setAllowFileAccess(true);\n"
        "        ws.setAllowContentAccess(true);\n"
        "        ws.setAllowFileAccessFromFileURLs(true);\n"
        "        ws.setAllowUniversalAccessFromFileURLs(true);\n"
        "        ws.setLoadWithOverviewMode(true);\n"
        "        ws.setUseWideViewPort(true);\n\n"
        "        webView.setWebViewClient(new WebViewClient());\n"
        "        webView.setWebChromeClient(new WebChromeClient());\n"
        "        webView.addJavascriptInterface(new NativeBridge(this), \"Android\");\n\n"
        "        try {\n"
        "            InputStream is = getAssets().open(\"index.html\");\n"
        "            ByteArrayOutputStream buffer = new ByteArrayOutputStream();\n"
        "            int nRead;\n"
        "            byte[] data = new byte[4096];\n"
        "            while ((nRead = is.read(data, 0, data.length)) != -1) {\n"
        "                buffer.write(data, 0, nRead);\n"
        "            }\n"
        "            is.close();\n"
        "            String htmlContent = buffer.toString(\"UTF-8\");\n"
        "            webView.loadDataWithBaseURL(\"https://localhost/\", htmlContent, \"text/html\", \"UTF-8\", null);\n"
        "        } catch (Exception e) {\n"
        "            webView.loadUrl(\"file:///android_asset/index.html\");\n"
        "        }\n"
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
        "        Context context;\n"
        "        NativeBridge(Context c) { context = c; }\n\n"
        "        @JavascriptInterface\n"
        "        public void showToast(String m) {\n"
        "            Toast.makeText(context, m, Toast.LENGTH_SHORT).show();\n"
        "        }\n\n"
        "        @JavascriptInterface\n"
        "        public void vibrate(long ms) {\n"
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
    print(f"[OK] Universal Native Shell siap untuk {clean_app_name} ({pkg})")


if __name__ == "__main__":
    main()
