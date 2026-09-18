# generate_project.py (Bagian template MainActivity.java & AndroidManifest.xml)

MAIN_ACTIVITY_JAVA = """package com.apkbuilder.app;

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

        // 1. Konfigurasi WebSettings Lengkap
        WebSettings ws = webView.getSettings();
        ws.setJavaScriptEnabled(true);
        ws.setDomStorageEnabled(true);              // WAJIB: Aktifkan localStorage & sessionStorage
        ws.setDatabaseEnabled(true);
        ws.setAllowFileAccess(true);
        ws.setAllowContentAccess(true);
        ws.setAllowFileAccessFromFileURLs(true);
        ws.setAllowUniversalAccessFromFileURLs(true);
        ws.setLoadWithOverviewMode(true);
        ws.setUseWideViewPort(true);
        ws.setSupportZoom(false);
        ws.setCacheMode(WebSettings.LOAD_DEFAULT);

        // 2. Aktifkan Hardware Acceleration pada WebView
        webView.setLayerType(View.LAYER_TYPE_HARDWARE, null);

        // 3. Tangkap Logcat Console agar error JS terlihat di Logcat Android
        webView.setWebChromeClient(new WebChromeClient() {
            @Override
            public boolean onConsoleMessage(ConsoleMessage cm) {
                Log.d("APK_JS_LOG", cm.message() + " [Line " + cm.lineNumber() + " of " + cm.sourceId() + "]");
                return true;
            }
        });

        webView.setWebViewClient(new WebViewClient() {
            @Override
            public void onReceivedError(WebView view, WebResourceRequest request, WebResourceError error) {
                Log.e("APK_WEB_ERROR", "Gagal memuat URL: " + error.getDescription());
            }
        });

        // 4. Muat HTML menggunakan loadDataWithBaseURL dengan Origin Lokal Standar
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

            // Gunakan skema https lokal agar localStorage terisolasi dengan aman tanpa diblokir
            webView.loadDataWithBaseURL("https://appassets.androidcache.local/", sb.toString(), "text/html", "UTF-8", null);
        } catch (Exception e) {
            Log.e("APK_LOAD_FAIL", "Fallback ke file URL asset", e);
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
"""

ANDROID_MANIFEST_XML = """<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    package="com.apkbuilder.app">

    <uses-permission android:name="android.permission.INTERNET" />
    <uses-permission android:name="android.permission.ACCESS_NETWORK_STATE" />

    <application
        android:allowBackup="true"
        android:label="GeneratedApp"
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
"""
