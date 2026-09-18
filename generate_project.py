#!/usr/bin/env python3
import sys
import os
import re
import base64
import time
import hashlib

def generate_android_project(app_name: str, html_b64: str):
    # 1. Sanitasi Nama Aplikasi
    safe_name = re.sub(r'[^a-zA-Z0-9]', '', app_name)
    if not safe_name:
        safe_name = "GeneratedApp"

    # 2. Buat Unique Package Name (Mencegah bentrok update di Android)
    clean_pkg_name = safe_name.lower()
    if not clean_pkg_name or clean_pkg_name[0].isdigit():
        clean_pkg_name = "app" + clean_pkg_name
        
    unique_hash = hashlib.md5(f"{clean_pkg_name}_{time.time()}".encode()).hexdigest()[:6]
    dynamic_package_id = f"com.apkbuilder.{clean_pkg_name}_{unique_hash}"

    # 3. Decode dan Verifikasi Konten HTML
    try:
        html_content = base64.b64decode(html_b64).decode("utf-8")
        if len(html_content.strip()) < 50:
            raise ValueError("HTML terlalu pendek")
    except Exception as e:
        print(f"[WARN] Gagal decode base64 atau HTML kosong ({e}). Menggunakan template darurat.")
        html_content = f"<!DOCTYPE html><html><head><meta name='viewport' content='width=device-width, initial-scale=1.0'></head><body style='background:#0F172A;color:white;display:flex;justify-content:center;align-items:center;height:100vh;font-family:sans-serif;'><h2>{safe_name} Siap Digunakan</h2></body></html>"

    print(f"[INFO] Ukuran file HTML: {len(html_content.encode('utf-8'))} bytes")

    # 4. Direktori Struktur Android
    dirs = [
        "app",
        "app/src/main/java/com/apkbuilder/app",
        "app/src/main/assets",
        "app/src/main/res/values",
        "app/src/main/res/drawable"
    ]
    for d in dirs:
        os.makedirs(d, exist_ok=True)

    # 5. Tulis index.html
    with open("app/src/main/assets/index.html", "w", encoding="utf-8") as f:
        f.write(html_content)

    # 6. Buat Vector Icon Aplikasi Modern (ic_launcher.xml)
    with open("app/src/main/res/drawable/ic_launcher.xml", "w", encoding="utf-8") as f:
        f.write("""<vector xmlns:android="http://schemas.android.com/apk/res/android"
    android:width="108dp"
    android:height="108dp"
    android:viewportWidth="108"
    android:viewportHeight="108">
    <!-- Background Circle Gelap Modern -->
    <path
        android:fillColor="#1E293B"
        android:pathData="M54,4 C26.39,4 4,26.39 4,54 C4,81.61 26.39,104 54,104 C81.61,104 104,81.61 104,54 C104,26.39 81.61,4 54,4 Z"/>
    <!-- Aksen Gadget / App Icon Cyan -->
    <path
        android:fillColor="#38BDF8"
        android:pathData="M38,28 L70,28 A6,6 0 0,1 76,34 L76,74 A6,6 0 0,1 70,80 L38,80 A6,6 0 0,1 32,74 L32,34 A6,6 0 0,1 38,28 Z"/>
    <!-- Layar Dalam -->
    <path
        android:fillColor="#0F172A"
        android:pathData="M36,36 L72,36 L72,68 L36,68 Z"/>
    <!-- Tombol Home / Aksen Bawah -->
    <path
        android:fillColor="#38BDF8"
        android:pathData="M54,74 A2,2 0 1,0 54,74.1 Z"/>
</vector>
""")

    # 7. settings.gradle (Root)
    with open("settings.gradle", "w", encoding="utf-8") as f:
        f.write('rootProject.name = "UniversalApp"\ninclude(":app")\n')

    # 8. build.gradle (Root)
    with open("build.gradle", "w", encoding="utf-8") as f:
        f.write("""buildscript {
    repositories {
        google()
        mavenCentral()
    }
    dependencies {
        classpath "com.android.tools.build:gradle:8.2.2"
    }
}
allprojects {
    repositories {
        google()
        mavenCentral()
    }
}
""")

    # 9. gradle.properties
    with open("gradle.properties", "w", encoding="utf-8") as f:
        f.write("""org.gradle.jvmargs=-Xmx2048m -Dfile.encoding=UTF-8
android.useAndroidX=true
android.nonTransitiveRClass=true
""")

    # 10. app/build.gradle (ApplicationId Dibuat Dinamis)
    with open("app/build.gradle", "w", encoding="utf-8") as f:
        f.write(f"""apply plugin: 'com.android.application'

android {{
    namespace 'com.apkbuilder.app'
    compileSdk 34

    defaultConfig {{
        applicationId "{dynamic_package_id}"
        minSdk 21
        targetSdk 34
        versionCode 1
        versionName "1.0"
    }}

    buildTypes {{
        release {{
            minifyEnabled false
        }}
        debug {{
            minifyEnabled false
        }}
    }}
    compileOptions {{
        sourceCompatibility JavaVersion.VERSION_17
        targetCompatibility JavaVersion.VERSION_17
    }}
}}

dependencies {{
    // Standalone engine tanpa library eksternal
}}
""")

    # 11. app/src/main/res/values/strings.xml
    with open("app/src/main/res/values/strings.xml", "w", encoding="utf-8") as f:
        f.write(f"""<resources>
    <string name="app_name">{safe_name}</string>
</resources>
""")

    # 12. app/src/main/AndroidManifest.xml (Didaftarkan Icon & Unique Package)
    with open("app/src/main/AndroidManifest.xml", "w", encoding="utf-8") as f:
        f.write("""<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android">

    <uses-permission android:name="android.permission.INTERNET" />
    <uses-permission android:name="android.permission.ACCESS_NETWORK_STATE" />

    <application
        android:allowBackup="true"
        android:label="@string/app_name"
        android:icon="@drawable/ic_launcher"
        android:roundIcon="@drawable/ic_launcher"
        android:supportsRtl="true"
        android:hardwareAccelerated="true"
        android:usesCleartextTraffic="true">
        
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

    # 13. app/src/main/java/com/apkbuilder/app/MainActivity.java
    with open("app/src/main/java/com/apkbuilder/app/MainActivity.java", "w", encoding="utf-8") as f:
        f.write("""package com.apkbuilder.app;

import android.annotation.SuppressLint;
import android.app.Activity;
import android.os.Bundle;
import android.util.Log;
import android.view.View;
import android.webkit.ConsoleMessage;
import android.webkit.WebChromeClient;
import android.webkit.WebResourceError;
import android.webkit.WebResourceRequest;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import java.io.BufferedReader;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;

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
        ws.setLoadWithOverviewMode(true);
        ws.setUseWideViewPort(true);
        ws.setSupportZoom(false);
        ws.setCacheMode(WebSettings.LOAD_DEFAULT);

        webView.setLayerType(View.LAYER_TYPE_HARDWARE, null);

        webView.setWebChromeClient(new WebChromeClient() {
            @Override
            public boolean onConsoleMessage(ConsoleMessage cm) {
                Log.d("APK_JS_LOG", cm.message() + " [Baris " + cm.lineNumber() + "]");
                return true;
            }
        });

        webView.setWebViewClient(new WebViewClient() {
            @Override
            public void onReceivedError(WebView view, WebResourceRequest request, WebResourceError error) {
                Log.e("APK_WEB_ERROR", "Gagal memuat URL: " + error.getDescription());
            }
        });

        try {
            InputStream is = getAssets().open("index.html");
            BufferedReader reader = new BufferedReader(new InputStreamReader(is, StandardCharsets.UTF_8));
            StringBuilder sb = new StringBuilder();
            String line;
            while ((line = reader.readLine()) != null) {
                sb.append(line).append("\\n");
            }
            reader.close();
            is.close();

            webView.loadDataWithBaseURL("https://appassets.androidcache.local/", sb.toString(), "text/html", "UTF-8", null);
        } catch (Exception e) {
            Log.e("APK_LOAD_FAIL", "Fallback loadUrl", e);
            webView.loadUrl("file:///android_asset/index.html");
        }
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

    print(f"[OK] Sukses merakit project. Package ID: {dynamic_package_id}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Penggunaan: python generate_project.py <APP_NAME> <HTML_BASE64>")
        sys.exit(1)

    app_name_arg = sys.argv[1]
    html_b64_arg = sys.argv[2]
    generate_android_project(app_name_arg, html_b64_arg)
