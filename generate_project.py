#!/usr/bin/env python3
"""
Universal Native Shell Generator (Hybrid Engine)
- Zero Javac Compilation Error: Java & Gradle 100% statis.
- Zero XML Resource Error: Tampilan dirender langsung via Native Engine.
- DOM Storage & IndexedDB Aktif: Data checklist / kasir tersimpan permanen di HP.
- Native Bridge: JavaScript dapat memanggil getar (vibrate) dan notifikasi (toast).
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


def die(msg, code=2):
    print(f"[FATAL] {msg}", file=sys.stderr)
    sys.exit(code)


def safe_get(d, keys, default=""):
    if not isinstance(d, dict):
        return default
    if isinstance(keys, str):
        keys = [keys]
    for k in keys:
        v = d.get(k)
        if v and isinstance(v, str) and v.strip():
            return v.strip()
    return default


def get_html_payload(d):
    """Membaca kode HTML dari bot STB (Base64 atau Plain Text)."""
    if not isinstance(d, dict):
        return ""

    # 1. Cek key Base64
    b64_keys = ["html_code_b64", "code_b64", "index_html_b64", "web_code_b64", "xml_code_b64"]
    for k in b64_keys:
        val = d.get(k)
        if val and isinstance(val, str) and val.strip():
            try:
                dec = base64.b64decode(val.strip()).decode("utf-8", errors="ignore")
                if dec.strip():
                    return dec.strip()
            except Exception:
                pass

    # 2. Cek key Plain Text
    plain_keys = ["html_code", "index_html", "code", "web_code", "activity_main_xml"]
    for k in plain_keys:
        val = d.get(k)
        if val and isinstance(val, str) and val.strip():
            s = val.strip()
            if len(s) > 50 and " " not in s and len(s) % 4 == 0:
                try:
                    dec = base64.b64decode(s).decode("utf-8", errors="ignore")
                    if LT in dec:
                        return dec.strip()
                except Exception:
                    pass
            return s

    return ""


# Template Default jika AI tidak mengirim HTML
DEFAULT_HTML = f"""<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
    <title>Dynamic App</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-slate-900 text-white min-h-screen flex flex-col items-center justify-center p-6 text-center">
    <div class="bg-slate-800 p-8 rounded-2xl shadow-xl border border-slate-700 max-w-sm w-full">
        <h1 class="text-2xl font-bold text-emerald-400 mb-2">Aplikasi Berhasil Dibuat!</h1>
        <p class="text-slate-300 text-sm mb-6">Engine Universal Native Shell telah aktif dan siap memuat UI modern.</p>
        <button onclick="if(window.Android) Android.showToast('Native Bridge Berfungsi!');" class="w-full py-3 bg-emerald-500 hover:bg-emerald-600 rounded-xl font-semibold shadow-lg active:scale-95 transition">Tes Native Toast</button>
    </div>
</body>
</html>"""

# Icon Bawaan Aplikasi
IC_LAUNCHER_XML = (
    f"{LT}?xml version=\"1.0\" encoding=\"utf-8\"?{GT}\n"
    f"{LT}vector xmlns:android=\"http://schemas.android.com/apk/res/android\"\n"
    f"    android:width=\"108dp\"\n"
    f"    android:height=\"108dp\"\n"
    f"    android:viewportWidth=\"108\"\n"
    f"    android:viewportHeight=\"108\"{GT}\n"
    f"    {LT}path android:fillColor=\"#0F172A\" android:pathData=\"M0,0h108v108h-108z\"/{GT}\n"
    f"    {LT}path android:fillColor=\"#10B981\" android:pathData=\"M54,20L74,40H60V74H48V40H34L54,20Z\"/{GT}\n"
    f"{LT}/vector{GT}\n"
)


def clean_html(code):
    """Membersihkan kode dari blok markdown backtick ```html ... ```."""
    if not code:
        return DEFAULT_HTML
    code = code.strip()
    code = re.sub(r"^```(?:html|xml)?\s*", "", code, flags=re.IGNORECASE)
    code = re.sub(r"\s*```$", "", code)
    if LT not in code:
        return DEFAULT_HTML
    return code


def write(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def main():
    if not PAYLOAD.exists():
        die("payload.json tidak ditemukan!")
    try:
        data = json.loads(PAYLOAD.read_text(encoding="utf-8"))
    except Exception as e:
        die(f"payload.json rusak: {e}")

    # 1. Bersihkan Nama Aplikasi
    raw_name = safe_get(data, ["app_name", "title", "name"], "DynamicApp")
    clean_app_name = re.sub(r"[^\w\s-]", "", raw_name).strip() or "DynamicApp"

    # 2. Package Name Unik
    pkg_suffix = re.sub(r"[^a-zA-Z0-9]", "", clean_app_name).lower()
    if len(pkg_suffix) < 3:
        pkg_suffix = "dynamicapp"
    pkg = f"com.stb.{pkg_suffix}"

    # 3. Baca Kode HTML Hasil AI
    raw_html = get_html_payload(data)
    final_html = clean_html(raw_html)

    print(f"[*] App Name        : {clean_app_name}")
    print(f"[*] Dynamic Package : {pkg}")
    print(f"[*] HTML Engine Size: {len(final_html)} bytes")

    # 4. Settings & Root Gradle
    write(ROOT / "settings.gradle", (
        "pluginManagement { repositories { google(); mavenCentral(); gradlePluginPortal() } }\n"
        "dependencyResolutionManagement { repositoriesMode.set(RepositoriesMode.PREFER_SETTINGS); repositories { google(); mavenCentral() } }\n"
        f"rootProject.name = '{pkg_suffix}'\n"
        "include ':app'\n"
    ))

    write(ROOT / "build.gradle", "plugins { id 'com.android.application' version '8.5.2' apply false }\n")

    write(ROOT / "gradle.properties", (
        "org.gradle.jvmargs=-Xmx2048m -Dfile.encoding=UTF-8\n"
        "android.useAndroidX=true\n"
        "android.nonTransitiveRClass=true\n"
    ))

    # 5. App Module Build Configuration (Tanpa dependensi berat, kompilasi super cepat)
    write(ROOT / "app" / "build.gradle", (
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
        "    }\n\n"
        "    buildTypes {\n"
        "        release { minifyEnabled false }\n"
        "    }\n"
        "    compileOptions {\n"
        "        sourceCompatibility JavaVersion.VERSION_17\n"
        "        targetCompatibility JavaVersion.VERSION_17\n"
        "    }\n"
        "}\n\n"
        "dependencies {\n"
        "    implementation 'androidx.annotation:annotation:1.9.1'\n"
        "}\n"
    ))

    # 6. AndroidManifest.xml (Full Izin: Internet, Storage, Vibrate)
    manifest = (
        f"{LT}?xml version=\"1.0\" encoding=\"utf-8\"?{GT}\n"
        f"{LT}manifest xmlns:android=\"http://schemas.android.com/apk/res/android\"{GT}\n"
        f"    {LT}uses-permission android:name=\"android.permission.INTERNET\" /{GT}\n"
        f"    {LT}uses-permission android:name=\"android.permission.ACCESS_NETWORK_STATE\" /{GT}\n"
        f"    {LT}uses-permission android:name=\"android.permission.VIBRATE\" /{GT}\n"
        f"    {LT}application\n"
        f"        android:allowBackup=\"true\"\n"
        f"        android:icon=\"@drawable/ic_launcher\"\n"
        f"        android:label=\"@string/app_name\"\n"
        f"        android:supportsRtl=\"true\"\n"
        f"        android:usesCleartextTraffic=\"true\"\n"
        f"        android:theme=\"@android:style/Theme.DeviceDefault.NoActionBar\"{GT}\n"
        f"        {LT}activity\n"
        f"            android:name=\".MainActivity\"\n"
        f"            android:configChanges=\"orientation|screenSize|keyboardHidden\"\n"
        f"            android:exported=\"true\"{GT}\n"
        f"            {LT}intent-filter{GT}\n"
        f"                {LT}action android:name=\"android.intent.action.MAIN\" /{GT}\n"
        f"                {LT}category android:name=\"android.intent.category.LAUNCHER\" /{GT}\n"
        f"            {LT}/intent-filter{GT}\n"
        f"        {LT}/activity{GT}\n"
        f"    {LT}/application{GT}\n"
        f"{LT}/manifest{GT}\n"
    )
    write(ROOT / "app" / "src" / "main" / "AndroidManifest.xml", manifest)

    # 7. Resources Paten
    strings_xml = (
        f"{LT}?xml version=\"1.0\" encoding=\"utf-8\"?{GT}\n"
        f"{LT}resources{GT}\n"
        f"    {LT}string name=\"app_name\"{GT}{clean_app_name}{LT}/string{GT}\n"
        f"{LT}/resources{GT}\n"
    )
    write(ROOT / "app" / "src" / "main" / "res" / "values" / "strings.xml", strings_xml)
    write(ROOT / "app" / "src" / "main" / "res" / "drawable" / "ic_launcher.xml", IC_LAUNCHER_XML)

    # 8. Tulis File HTML AI ke dalam Asset HP
    write(ROOT / "app" / "src" / "main" / "assets" / "index.html", final_html)

    # 9. Java Universal Shell Statis (100% Kebal Error)
    java_code = (
        f"package {pkg};\n\n"
        "import android.app.Activity;\n"
        "import android.content.Context;\n"
        "import android.os.Bundle;\n"
        "import android.os.Vibrator;\n"
        "import android.webkit.JavascriptInterface;\n"
        "import android.webkit.WebChromeClient;\n"
        "import android.webkit.WebSettings;\n"
        "import android.webkit.WebView;\n"
        "import android.webkit.WebViewClient;\n"
        "import android.widget.Toast;\n\n"
        "public class MainActivity extends Activity {\n"
        "    private WebView webView;\n\n"
        "    @Override\n"
        "    protected void onCreate(Bundle savedInstanceState) {\n"
        "        super.onCreate(savedInstanceState);\n"
        "        webView = new WebView(this);\n"
        "        setContentView(webView);\n\n"
        "        WebSettings ws = webView.getSettings();\n"
        "        ws.setJavaScriptEnabled(true);\n"
        "        ws.setDomStorageEnabled(true);\n"
        "        ws.setDatabaseEnabled(true);\n"
        "        ws.setAllowFileAccess(true);\n"
        "        ws.setAllowContentAccess(true);\n"
        "        ws.setLoadWithOverviewMode(true);\n"
        "        ws.setUseWideViewPort(true);\n"
        "        ws.setCacheMode(WebSettings.LOAD_DEFAULT);\n\n"
        "        webView.setWebViewClient(new WebViewClient());\n"
        "        webView.setWebChromeClient(new WebChromeClient());\n"
        "        webView.addJavascriptInterface(new NativeBridge(this), \"Android\");\n\n"
        "        webView.loadUrl(\"file:///android_asset/index.html\");\n"
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
        "        public void showToast(String msg) {\n"
        "            Toast.makeText(context, msg, Toast.LENGTH_SHORT).show();\n"
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

    java_path = ROOT / "app" / "src" / "main" / "java" / pathlib.Path(*pkg.split("."))
    write(java_path / "MainActivity.java", java_code)

    print(f"[OK] Universal Native Shell siap dikompilasi untuk {clean_app_name} ({pkg})!")


if __name__ == "__main__":
    main()
