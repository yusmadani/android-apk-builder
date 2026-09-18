#!/usr/bin/env python3
import sys
import os
import re
import base64
import time
import hashlib
import urllib.request

def inject_heavy_assets(target_asset_dir: str, engine_type: str):
    """
    Menyuntikkan pustaka besar, modul WebGL, model 3D, 
    atau asset binary offline langsung ke folder assets APK.
    """
    print(f"[ASSET] Menyiapkan modul aset untuk tipe: {engine_type}...")

    # Folder pustaka offline di dalam assets
    vendor_dir = os.path.join(target_asset_dir, "vendor")
    os.makedirs(vendor_dir, exist_ok=True)

    # Contoh dependensi 3D & Audio yang disematkan lokal (Zero-Internet Runtime)
    asset_manifest = {
        # Engine 3D Standalone (Three.js Bundle + OrbitControls)
        "three.min.js": "https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js",
        # Framework UI Offline CSS murni berukuran lengkap
        "bootstrap.min.css": "https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css",
        # Engine Fisika 2D / 3D lokal (Cannon / Matter)
        "cannon.min.js": "https://cdnjs.cloudflare.com/ajax/libs/cannon.js/0.6.2/cannon.min.js"
    }

    # Unduh setiap dependensi berat ke dalam APK
    for filename, url in asset_manifest.items():
        dest = os.path.join(vendor_dir, filename)
        if not os.path.exists(dest):
            try:
                print(f"[ASSET] Mengunduh {filename}...")
                urllib.request.urlretrieve(url, dest)
            except Exception as e:
                print(f"[WARN] Gagal mengunduh {filename}: {e}")

    # Jika butuh aset ratusan MB (misal dataset SQLite / Audio bank dummy / Texture pack)
    if engine_type == "3d_game" or engine_type == "heavy":
        data_file = os.path.join(target_asset_dir, "data_pack.bin")
        if not os.path.exists(data_file):
            print("[ASSET] Membangun alokasi asset binary pack...")
            # Contoh pembuatan blob aset lokal berukuran besar
            with open(data_file, "wb") as f:
                f.write(os.urandom(50 * 1024 * 1024)) # 50 MB buffer pack contoh

def generate_android_project(app_name: str, html_b64: str, engine_type: str = "default"):
    safe_name = re.sub(r'[^a-zA-Z0-9]', '', app_name) or "HeavyApp"
    clean_pkg = safe_name.lower()
    if clean_pkg[0].isdigit():
        clean_pkg = "app" + clean_pkg
        
    unique_hash = hashlib.md5(f"{clean_pkg}_{time.time()}".encode()).hexdigest()[:6]
    package_id = f"com.apkbuilder.{clean_pkg}_{unique_hash}"

    # Decode HTML
    try:
        html_content = base64.b64decode(html_b64).decode("utf-8")
    except Exception:
        html_content = "<!DOCTYPE html><html><body><h1>Inisialisasi Gagal</h1></body></html>"

    assets_path = "app/src/main/assets"
    os.makedirs(f"app/src/main/java/com/apkbuilder/app", exist_ok=True)
    os.makedirs(assets_path, exist_ok=True)
    os.makedirs("app/src/main/res/values", exist_ok=True)
    os.makedirs("app/src/main/res/drawable", exist_ok=True)

    # 1. Tulis index.html
    with open(f"{assets_path}/index.html", "w", encoding="utf-8") as f:
        f.write(html_content)

    # 2. Suntikkan Aset Berat (Engine, CSS Offline, Sound, Texture)
    inject_heavy_assets(assets_path, engine_type)

    # 3. Vector Icon
    with open("app/src/main/res/drawable/ic_launcher.xml", "w", encoding="utf-8") as f:
        f.write("""<vector xmlns:android="http://schemas.android.com/apk/res/android"
    android:width="108dp" android:height="108dp" android:viewportWidth="108" android:viewportHeight="108">
    <path android:fillColor="#1E293B" android:pathData="M54,4 C26.39,4 4,26.39 4,54 C4,81.61 26.39,104 54,104 C81.61,104 104,81.61 104,54 C104,26.39 81.61,4 54,4 Z"/>
    <path android:fillColor="#F43F5E" android:pathData="M38,28 L70,28 A6,6 0 0,1 76,34 L76,74 A6,6 0 0,1 70,80 L38,80 A6,6 0 0,1 32,74 L32,34 A6,6 0 0,1 38,28 Z"/>
</vector>""")

    # 4. Settings & Root Gradle
    with open("settings.gradle", "w", encoding="utf-8") as f:
        f.write('rootProject.name = "UniversalHeavyApp"\ninclude(":app")\n')

    with open("build.gradle", "w", encoding="utf-8") as f:
        f.write("""buildscript {
    repositories { google(); mavenCentral() }
    dependencies { classpath "com.android.tools.build:gradle:8.2.2" }
}
allprojects {
    repositories { google(); mavenCentral() }
}
""")

    with open("gradle.properties", "w", encoding="utf-8") as f:
        f.write("org.gradle.jvmargs=-Xmx4096m -Dfile.encoding=UTF-8\nandroid.useAndroidX=true\n")

    # 5. app/build.gradle (Alokasikan Memori Besar untuk APK Jumbo)
    with open("app/build.gradle", "w", encoding="utf-8") as f:
        f.write(f"""apply plugin: 'com.android.application'

android {{
    namespace 'com.apkbuilder.app'
    compileSdk 34

    defaultConfig {{
        applicationId "{package_id}"
        minSdk 21
        targetSdk 34
        versionCode 1
        versionName "1.0"
    }}

    aaptOptions {{
        // Cegah kompresi ganda pada asset binary raksasa agar tidak crash saat compile
        noCompress ''
    }}

    buildTypes {{
        debug {{ minifyEnabled false }}
        release {{ minifyEnabled false }}
    }}
    compileOptions {{
        sourceCompatibility JavaVersion.VERSION_17
        targetCompatibility JavaVersion.VERSION_17
    }}
}}
""")

    # 6. Manifest & Strings
    with open("app/src/main/res/values/strings.xml", "w", encoding="utf-8") as f:
        f.write(f'<resources><string name="app_name">{safe_name}</string></resources>')

    with open("app/src/main/AndroidManifest.xml", "w", encoding="utf-8") as f:
        f.write("""<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android">
    <uses-permission android:name="android.permission.INTERNET" />
    <uses-permission android:name="android.permission.ACCESS_NETWORK_STATE" />
    <application
        android:allowBackup="true"
        android:label="@string/app_name"
        android:icon="@drawable/ic_launcher"
        android:hardwareAccelerated="true"
        android:largeHeap="true">
        <activity
            android:name="com.apkbuilder.app.MainActivity"
            android:exported="true"
            android:configChanges="orientation|screenSize|keyboardHidden"
            android:theme="@android:style/Theme.NoTitleBar.Fullscreen">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>
    </application>
</manifest>
""")

    # 7. MainActivity (Tangguh menangani Aset Besar & WebGL)
    with open("app/src/main/java/com/apkbuilder/app/MainActivity.java", "w", encoding="utf-8") as f:
        f.write("""package com.apkbuilder.app;

import android.annotation.SuppressLint;
import android.app.Activity;
import android.os.Bundle;
import android.view.View;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;

public class MainActivity extends Activity {
    private WebView webView;

    @SuppressLint("SetJavaScriptEnabled")
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        webView = new WebView(this);
        setContentView(webView);

        WebSettings ws = webView.getSettings();
        ws.setJavaScriptEnabled(true);
        ws.setDomStorageEnabled(true);
        ws.setDatabaseEnabled(true);
        ws.setAllowFileAccess(true);
        ws.setAllowContentAccess(true);
        ws.setAllowFileAccessFromFileURLs(true);
        ws.setAllowUniversalAccessFromFileURLs(true);
        ws.setMediaPlaybackRequiresUserGesture(false);

        webView.setLayerType(View.LAYER_TYPE_HARDWARE, null);
        webView.setWebViewClient(new WebViewClient());

        // Muat langsung dari root assets agar file vendor/ dapat diakses via path relatif
        webView.loadUrl("file:///android_asset/index.html");
    }

    @Override
    public void onBackPressed() {
        if (webView != null && webView.canGoBack()) {
            webView.goBack();
        } else {
            super.onBackPressed();
        }
    }
}
""")
    print(f"[OK] Sukses merakit proyek Android skala besar: {package_id}")

if __name__ == "__main__":
    name = sys.argv[1] if len(sys.argv) > 1 else "HeavyApp"
    code = sys.argv[2] if len(sys.argv) > 2 else ""
    eng = sys.argv[3] if len(sys.argv) > 3 else "default"
    generate_android_project(name, code, eng)
