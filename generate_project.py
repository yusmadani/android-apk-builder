#!/usr/bin/env python3
import sys
import os
import re
import base64

def generate_android_project(app_name: str, html_b64: str):
    # Bersihkan nama aplikasi untuk identifier Java/XML
    safe_name = re.sub(r'[^a-zA-Z0-9]', '', app_name)
    if not safe_name:
        safe_name = "GeneratedApp"

    # Decode HTML
    try:
        html_content = base64.b64decode(html_b64).decode("utf-8")
    except Exception:
        html_content = "<!DOCTYPE html><html><body><h1>Aplikasi Gagal Dimuat</h1></body></html>"

    # Direktori struktur Android standar
    dirs = [
        "app",
        "app/src/main/java/com/apkbuilder/app",
        "app/src/main/assets",
        "app/src/main/res/values",
        "app/src/main/res/mipmap-hdpi"
    ]
    for d in dirs:
        os.makedirs(d, exist_ok=True)

    # 1. Simpan index.html ke folder assets
    with open("app/src/main/assets/index.html", "w", encoding="utf-8") as f:
        f.write(html_content)

    # 2. settings.gradle (Root)
    with open("settings.gradle", "w", encoding="utf-8") as f:
        f.write('rootProject.name = "UniversalApp"\ninclude(":app")\n')

    # 3. build.gradle (Root)
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

    # 4. gradle.properties
    with open("gradle.properties", "w", encoding="utf-8") as f:
        f.write("""org.gradle.jvmargs=-Xmx2048m -Dfile.encoding=UTF-8
android.useAndroidX=true
android.nonTransitiveRClass=true
""")

    # 5. app/build.gradle
    with open("app/build.gradle", "w", encoding="utf-8") as f:
        f.write("""apply plugin: 'com.android.application'

android {
    namespace 'com.apkbuilder.app'
    compileSdk 34

    defaultConfig {
        applicationId "com.apkbuilder.app"
        minSdk 21
        targetSdk 34
        versionCode 1
        versionName "1.0"
    }

    buildTypes {
        release {
            minifyEnabled false
        }
        debug {
            minifyEnabled false
        }
    }
    compileOptions {
        sourceCompatibility JavaVersion.VERSION_17
        targetCompatibility JavaVersion.VERSION_17
    }
}

dependencies {
    // Tanpa library berat eksternal agar build secepat kilat & zero compile error
}
""")

    # 6. app/src/main/res/values/strings.xml
    with open("app/src/main/res/values/strings.xml", "w", encoding="utf-8") as f:
        f.write(f"""<resources>
    <string name="app_name">{safe_name}</string>
</resources>
""")

    # 7. app/src/main/AndroidManifest.xml
    with open("app/src/main/AndroidManifest.xml", "w", encoding="utf-8") as f:
        f.write("""<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    package="com.apkbuilder.app">

    <uses-permission android:name="android.permission.INTERNET" />
    <uses-permission android:name="android.permission.ACCESS_NETWORK_STATE" />

    <application
        android:allowBackup="true"
        android:label="@string/app_name"
        android:supportsRtl="true"
        android:hardwareAccelerated="true"
        android:usesCleartextTraffic="true">
        
        <activity
            android:name=".MainActivity"
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

    # 8. app/src/main/java/com/apkbuilder/app/MainActivity.java
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

        // Pengaturan WebView tangguh anti-blank
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

        // Hardware acceleration level layer
        webView.setLayerType(View.LAYER_TYPE_HARDWARE, null);

        // Monitoring Logcat
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

        // Muat file index.html dari folder assets
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
            Log.e("APK_LOAD_FAIL", "Gagal loadDataWithBaseURL, fallback ke direct file URL", e);
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

    print(f"[OK] Sukses merakit project Android untuk aplikasi: {safe_name}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Penggunaan: python generate_project.py <APP_NAME> <HTML_BASE64>")
        sys.exit(1)

    app_name_arg = sys.argv[1]
    html_b64_arg = sys.argv[2]
    generate_android_project(app_name_arg, html_b64_arg)
