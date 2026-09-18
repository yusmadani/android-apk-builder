#!/usr/bin/env python3
"""
React Native + Meta Hermes Workspace Generator (Clean & Robust Edition)
- Solves Babel transformer / Metro parseSync issues.
- Sets up proper babel.config.js and metro.config.js.
- Generates 60 FPS Native Android harness with Hermes AOT Bytecode.
"""
import base64
import json
import os
import pathlib
import re
import sys

ROOT = pathlib.Path(".")
PAYLOAD = pathlib.Path("payload.json")

def write(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")

BASE_REACT_NATIVE_APP = """import React, { useState, useEffect } from 'react';
import {
  SafeAreaView,
  View,
  Text,
  TouchableOpacity,
  ScrollView,
  StyleSheet,
  StatusBar,
  Vibration,
  Alert
} from 'react-native';

const INITIAL_SCHEDULE = [
  { id: 1, time: '07:15 - 08:45', title: 'Pemrograman Web & Mobile', sub: 'Kelas XII RPL 1 • Lab Software', done: false },
  { id: 2, time: '09:00 - 10:30', title: 'Basis Data Terdistribusi', sub: 'Kelas XI RPL 2 • Lab Rekayasa', done: false },
  { id: 3, time: '10:45 - 12:15', title: 'Pemodelan Perangkat Lunak', sub: 'Kelas X RPL 1 • Ruang Teori 04', done: true },
  { id: 4, time: '13:00 - 14:30', title: 'Administrasi Infrastruktur Jaringan', sub: 'Kelas XII TKJ 2 • Bengkel TKJ', done: false }
];

export default function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [items, setItems] = useState(INITIAL_SCHEDULE);
  const [currentTime, setCurrentTime] = useState('');

  useEffect(() => {
    const updateTime = () => {
      const d = new Date();
      const hh = String(d.getHours()).padStart(2, '0');
      const mm = String(d.getMinutes()).padStart(2, '0');
      const ss = String(d.getSeconds()).padStart(2, '0');
      setCurrentTime(hh + ':' + mm + ':' + ss);
    };
    updateTime();
    const timer = setInterval(updateTime, 1000);
    return () => clearInterval(timer);
  }, []);

  const toggleItem = (id) => {
    try { Vibration.vibrate(35); } catch (e) {}
    setItems(prev => prev.map(item => item.id === id ? { ...item, done: !item.done } : item));
  };

  const completedCount = items.filter(i => i.done).length;
  const progressPercent = items.length > 0 ? Math.round((completedCount / items.length) * 100) : 0;

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar barStyle="light-content" backgroundColor="#070D18" />
      
      <View style={styles.header}>
        <View>
          <Text style={styles.headerTitle}>__APP_TITLE__</Text>
          <Text style={styles.headerSubtitle}>Hermes Engine • 60 FPS Native</Text>
        </View>
        <View style={styles.clockBadge}>
          <Text style={styles.clockText}>{currentTime || '00:00:00'}</Text>
        </View>
      </View>

      <ScrollView contentContainerStyle={styles.scrollContent}>
        {activeTab === 'dashboard' && (
          <View>
            <View style={styles.card}>
              <View style={styles.rowBetween}>
                <Text style={styles.cardHeader}>Capaian Aktivitas</Text>
                <Text style={styles.statNeon}>{progressPercent}%</Text>
              </View>
              <View style={styles.progressBarBg}>
                <View style={[styles.progressBarFill, { width: progressPercent + '%' }]} />
              </View>
              <View style={styles.statGrid}>
                <View style={styles.statBox}>
                  <Text style={styles.statNum}>{items.length}</Text>
                  <Text style={styles.statLabel}>Total Agenda</Text>
                </View>
                <View style={styles.statBox}>
                  <Text style={[styles.statNum, { color: '#00D4AA' }]}>{completedCount}</Text>
                  <Text style={styles.statLabel}>Selesai</Text>
                </View>
                <View style={styles.statBox}>
                  <Text style={[styles.statNum, { color: '#FF00FF' }]}>{items.length - completedCount}</Text>
                  <Text style={styles.statLabel}>Tertunda</Text>
                </View>
              </View>
            </View>

            <Text style={styles.sectionTitle}>Agenda Terjadwal Hari Ini</Text>
            {items.map(item => (
              <TouchableOpacity
                key={item.id}
                style={[styles.itemCard, item.done && styles.itemCardDone]}
                activeOpacity={0.8}
                onPress={() => toggleItem(item.id)}
              >
                <View style={{ flex: 1 }}>
                  <Text style={styles.itemBadge}>{item.time}</Text>
                  <Text style={[styles.itemTitle, item.done && styles.itemTitleDone]}>{item.title}</Text>
                  <Text style={styles.itemSub}>{item.sub}</Text>
                </View>
                <View style={[styles.checkBtn, item.done && styles.checkBtnDone]}>
                  <Text style={styles.checkBtnText}>{item.done ? '✓' : 'O'}</Text>
                </View>
              </TouchableOpacity>
            ))}
          </View>
        )}

        {activeTab === 'kelola' && (
          <View>
            <View style={styles.card}>
              <Text style={styles.cardHeader}>Manajemen Master Data</Text>
              <Text style={styles.infoText}>Modul sinkronisasi offline Hermes aktif. Semua perubahan tersimpan instan di level thread native.</Text>
              <TouchableOpacity
                style={styles.actionBtn}
                onPress={() => {
                  try { Vibration.vibrate(40); } catch (e) {}
                  Alert.alert('Sinkronisasi', 'Semua entri berhasil diperbarui ke database lokal.');
                }}
              >
                <Text style={styles.actionBtnText}>SINKRONISASI DATA</Text>
              </TouchableOpacity>
            </View>
          </View>
        )}

        {activeTab === 'analisis' && (
          <View>
            <View style={styles.card}>
              <Text style={styles.cardHeader}>Performa & Ringkasan</Text>
              <Text style={styles.infoText}>• Efektivitas Jam Aktif: 94.2%</Text>
              <Text style={styles.infoText}>• Waktu Respon UI: &lt; 16ms (Jank-Free)</Text>
              <Text style={styles.infoText}>• Bytecode Engine: Meta Hermes AOT Enabled</Text>
            </View>
          </View>
        )}
      </ScrollView>

      <View style={styles.tabBar}>
        <TouchableOpacity
          style={styles.tabItem}
          onPress={() => { try { Vibration.vibrate(20); } catch (e) {} setActiveTab('dashboard'); }}
        >
          <Text style={[styles.tabText, activeTab === 'dashboard' && styles.tabTextActive]}>DASHBOARD</Text>
        </TouchableOpacity>
        <TouchableOpacity
          style={styles.tabItem}
          onPress={() => { try { Vibration.vibrate(20); } catch (e) {} setActiveTab('kelola'); }}
        >
          <Text style={[styles.tabText, activeTab === 'kelola' && styles.tabTextActive]}>KELOLA</Text>
        </TouchableOpacity>
        <TouchableOpacity
          style={styles.tabItem}
          onPress={() => { try { Vibration.vibrate(20); } catch (e) {} setActiveTab('analisis'); }}
        >
          <Text style={[styles.tabText, activeTab === 'analisis' && styles.tabTextActive]}>ANALISIS</Text>
        </TouchableOpacity>
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#070D18'
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 20,
    paddingVertical: 16,
    borderBottomWidth: 1,
    borderBottomColor: 'rgba(0, 212, 170, 0.15)',
    backgroundColor: '#0B1424'
  },
  headerTitle: {
    fontSize: 20,
    fontWeight: '800',
    color: '#00D4AA',
    letterSpacing: -0.3
  },
  headerSubtitle: {
    fontSize: 11,
    color: '#8EA5C8',
    marginTop: 2
  },
  clockBadge: {
    backgroundColor: 'rgba(0, 212, 170, 0.12)',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: 'rgba(0, 212, 170, 0.3)'
  },
  clockText: {
    color: '#00D4AA',
    fontWeight: '700',
    fontSize: 13
  },
  scrollContent: {
    padding: 16,
    paddingBottom: 90
  },
  card: {
    backgroundColor: '#0F2744',
    borderRadius: 18,
    padding: 18,
    marginBottom: 16,
    borderWidth: 1,
    borderColor: 'rgba(255, 255, 255, 0.08)'
  },
  rowBetween: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center'
  },
  cardHeader: {
    fontSize: 16,
    fontWeight: '700',
    color: '#FFFFFF'
  },
  statNeon: {
    fontSize: 22,
    fontWeight: '900',
    color: '#00D4AA'
  },
  progressBarBg: {
    height: 8,
    backgroundColor: 'rgba(255, 255, 255, 0.08)',
    borderRadius: 4,
    marginVertical: 12,
    overflow: 'hidden'
  },
  progressBarFill: {
    height: '100%',
    backgroundColor: '#00D4AA',
    borderRadius: 4
  },
  statGrid: {
    flexDirection: 'row',
    gap: 8,
    marginTop: 8
  },
  statBox: {
    flex: 1,
    backgroundColor: 'rgba(7, 13, 24, 0.6)',
    padding: 12,
    borderRadius: 12,
    alignItems: 'center'
  },
  statNum: {
    fontSize: 18,
    fontWeight: '800',
    color: '#FFFFFF'
  },
  statLabel: {
    fontSize: 10,
    color: '#8EA5C8',
    marginTop: 2,
    textTransform: 'uppercase'
  },
  sectionTitle: {
    fontSize: 15,
    fontWeight: '700',
    color: '#00D4AA',
    marginBottom: 12,
    letterSpacing: 0.5
  },
  itemCard: {
    backgroundColor: '#0F2744',
    borderRadius: 14,
    padding: 16,
    marginBottom: 10,
    flexDirection: 'row',
    alignItems: 'center',
    borderWidth: 1,
    borderColor: 'rgba(255, 255, 255, 0.05)'
  },
  itemCardDone: {
    opacity: 0.55,
    borderColor: 'rgba(0, 212, 170, 0.3)'
  },
  itemBadge: {
    fontSize: 11,
    color: '#00D4AA',
    fontWeight: '700',
    marginBottom: 4
  },
  itemTitle: {
    fontSize: 15,
    fontWeight: '700',
    color: '#FFFFFF'
  },
  itemTitleDone: {
    textDecorationLine: 'line-through'
  },
  itemSub: {
    fontSize: 12,
    color: '#8EA5C8',
    marginTop: 2
  },
  checkBtn: {
    width: 38,
    height: 38,
    borderRadius: 10,
    backgroundColor: 'rgba(255, 255, 255, 0.08)',
    justifyContent: 'center',
    alignItems: 'center',
    marginLeft: 12
  },
  checkBtnDone: {
    backgroundColor: '#00D4AA'
  },
  checkBtnText: {
    color: '#FFFFFF',
    fontWeight: '800'
  },
  actionBtn: {
    backgroundColor: '#00D4AA',
    paddingVertical: 14,
    borderRadius: 12,
    alignItems: 'center',
    marginTop: 16
  },
  actionBtnText: {
    color: '#070D18',
    fontWeight: '800',
    fontSize: 14
  },
  infoText: {
    fontSize: 13,
    color: '#8EA5C8',
    marginTop: 8,
    lineHeight: 20
  },
  tabBar: {
    position: 'absolute',
    bottom: 0,
    left: 0,
    right: 0,
    height: 64,
    backgroundColor: '#0B1424',
    flexDirection: 'row',
    borderTopWidth: 1,
    borderTopColor: 'rgba(255, 255, 255, 0.08)'
  },
  tabItem: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center'
  },
  tabText: {
    fontSize: 12,
    fontWeight: '700',
    color: '#8EA5C8'
  },
  tabTextActive: {
    color: '#00D4AA'
  }
});
"""

def clean_user_jsx(code):
    if not code:
        return ""
    c = code.strip()
    c = re.sub(r"^```(?:javascript|jsx|tsx|js)?\s*", "", c, flags=re.IGNORECASE)
    c = re.sub(r"\s*```$", "", c)
    # Validasi bahwa kode benar-benar kode React Native
    if "import React" in c and ("<View" in c or "<SafeAreaView" in c) and "export default" in c:
        return c
    return ""

def main():
    raw_name = "Jadwal Mengajar"
    b64 = None

    if len(sys.argv) >= 3:
        raw_name = sys.argv[1]
        b64 = sys.argv[2]
    elif PAYLOAD.exists():
        try:
            data = json.loads(PAYLOAD.read_text(encoding="utf-8"))
            raw_name = data.get("app_name", "Jadwal Mengajar")
            b64 = data.get("html_code_b64") or data.get("code_b64")
        except Exception:
            pass

    clean_name = re.sub(r"[^\w\s-]", "", raw_name).strip() or "Jadwal Mengajar"
    pkg_suffix = re.sub(r"[^a-zA-Z0-9]", "", clean_name).lower() or "jadwalapp"
    pkg = f"com.centoa.{pkg_suffix}"

    user_code = ""
    if b64:
        try:
            decoded = base64.b64decode(b64).decode("utf-8", errors="ignore")
            user_code = clean_user_jsx(decoded)
        except Exception:
            user_code = ""

    if not user_code:
        app_js_content = BASE_REACT_NATIVE_APP.replace("__APP_TITLE__", clean_name)
    else:
        app_js_content = user_code

    # 1. Root React Native Files & Configurations
    write(ROOT / "package.json", json.dumps({
        "name": pkg_suffix,
        "version": "1.5.0",
        "private": True,
        "scripts": {
            "android": "react-native run-android"
        },
        "dependencies": {
            "react": "18.2.0",
            "react-native": "0.73.6"
        },
        "devDependencies": {
            "@babel/core": "^7.20.0",
            "@babel/preset-env": "^7.20.0",
            "@react-native/babel-preset": "0.73.21",
            "@react-native/metro-config": "0.73.5",
            "metro-react-native-babel-preset": "^0.77.0"
        }
    }, indent=2))

    # Babel config yang kompatibel dengan Metro Transformer Worker
    write(ROOT / "babel.config.js", (
        "module.exports = {\n"
        "  presets: ['module:@react-native/babel-preset'],\n"
        "};\n"
    ))

    write(ROOT / "index.js", (
        "import {AppRegistry} from 'react-native';\n"
        "import App from './App';\n"
        f"AppRegistry.registerComponent('{pkg_suffix}', () => App);\n"
    ))

    write(ROOT / "App.js", app_js_content)

    write(ROOT / "metro.config.js", (
        "const {getDefaultConfig, mergeConfig} = require('@react-native/metro-config');\n"
        "const config = {};\n"
        "module.exports = mergeConfig(getDefaultConfig(__dirname), config);\n"
    ))

    # 2. Android Native Harness with Hermes AOT Enabled
    android_dir = ROOT / "android"

    write(android_dir / "gradle" / "wrapper" / "gradle-wrapper.properties", (
        "distributionBase=GRADLE_USER_HOME\n"
        "distributionPath=wrapper/dists\n"
        "distributionUrl=https\\://services.gradle.org/distributions/gradle-8.7-bin.zip\n"
        "zipStoreBase=GRADLE_USER_HOME\n"
        "zipStorePath=wrapper/dists\n"
    ))

    write(android_dir / "settings.gradle", (
        f"rootProject.name = '{pkg_suffix}'\n"
        "apply from: file('../node_modules/@react-native-community/cli-platform-android/native_modules.gradle');\n"
        "applyNativeModulesSettingsGradle(settings)\n"
        "include ':app'\n"
        "includeBuild('../node_modules/@react-native/gradle-plugin')\n"
    ))

    write(android_dir / "build.gradle", (
        "buildscript {\n"
        "    ext {\n"
        "        buildToolsVersion = '34.0.0'\n"
        "        minSdkVersion = 24\n"
        "        compileSdkVersion = 34\n"
        "        targetSdkVersion = 34\n"
        "        ndkVersion = '25.1.8937393'\n"
        "        kotlinVersion = '1.9.22'\n"
        "    }\n"
        "    repositories { google(); mavenCentral() }\n"
        "    dependencies {\n"
        "        classpath('com.android.tools.build:gradle:8.5.2')\n"
        "        classpath('com.facebook.react:react-native-gradle-plugin')\n"
        "        classpath('org.jetbrains.kotlin:kotlin-gradle-plugin')\n"
        "    }\n"
        "}\n"
        "allprojects { repositories { google(); mavenCentral() } }\n"
    ))

    write(android_dir / "gradle.properties", (
        "org.gradle.jvmargs=-Xmx3072m -Dfile.encoding=UTF-8\n"
        "android.useAndroidX=true\n"
        "android.nonTransitiveRClass=true\n"
        "react.internal.disableAapt2=false\n"
    ))

    # Hermes diaktifkan di app/build.gradle
    write(android_dir / "app" / "build.gradle", (
        "apply plugin: 'com.android.application'\n"
        "apply plugin: 'org.jetbrains.kotlin.android'\n"
        "apply plugin: 'com.facebook.react'\n\n"
        "react {\n"
        "    hermesEnabled = true\n"
        "}\n\n"
        "android {\n"
        f"    namespace '{pkg}'\n"
        "    compileSdk rootProject.ext.compileSdkVersion\n"
        "    defaultConfig {\n"
        f"        applicationId '{pkg}'\n"
        "        minSdkVersion rootProject.ext.minSdkVersion\n"
        "        targetSdkVersion rootProject.ext.targetSdkVersion\n"
        "        versionCode 1\n"
        "        versionName '1.5'\n"
        "    }\n"
        "    buildTypes {\n"
        "        release {\n"
        "            signingConfig signingConfigs.debug\n"
        "            minifyEnabled false\n"
        "        }\n"
        "    }\n"
        "}\n\n"
        "dependencies {\n"
        "    implementation('com.facebook.react:react-android')\n"
        "    implementation('com.facebook.react:hermes-android')\n"
        "}\n"
    ))

    # 3. Android Manifest
    write(android_dir / "app" / "src" / "main" / "AndroidManifest.xml", (
        f"{chr(60)}manifest xmlns:android=\"http://schemas.android.com/apk/res/android\"{chr(62)}\n"
        f'    {chr(60)}uses-permission android:name="android.permission.INTERNET" /{chr(62)}\n'
        f'    {chr(60)}uses-permission android:name="android.permission.VIBRATE" /{chr(62)}\n'
        f"    {chr(60)}application\n"
        f'        android:name=".MainApplication"\n'
        f'        android:label="@string/app_name"\n'
        f'        android:icon="@mipmap/ic_launcher"\n'
        f'        android:theme="@style/AppTheme"{chr(62)}\n'
        f"        {chr(60)}activity\n"
        f'            android:name=".MainActivity"\n'
        f'            android:label="@string/app_name"\n'
        f'            android:configChanges="keyboard|keyboardHidden|orientation|screenLayout|screenSize|smallestScreenSize|uiMode"\n'
        f'            android:launchMode="singleTask"\n'
        f'            android:windowSoftInputMode="adjustResize"\n'
        f'            android:exported="true"{chr(62)}\n'
        f"            {chr(60)}intent-filter{chr(62)}\n"
        f'                {chr(60)}action android:name="android.intent.action.MAIN" /{chr(62)}\n'
        f'                {chr(60)}category android:name="android.intent.category.LAUNCHER" /{chr(62)}\n'
        f"            {chr(60)}/intent-filter{chr(62)}\n"
        f"        {chr(60)}/activity{chr(62)}\n"
        f"    {chr(60)}/application{chr(62)}\n"
        f"{chr(60)}/manifest{chr(62)}\n"
    ))

    # 4. Resources
    write(android_dir / "app" / "src" / "main" / "res" / "values" / "strings.xml",
        f'{chr(60)}resources{chr(62)}{chr(60)}string name="app_name"{chr(62)}{clean_name}{chr(60)}/string{chr(62)}{chr(60)}/resources{chr(62)}'
    )
    write(android_dir / "app" / "src" / "main" / "res" / "values" / "styles.xml",
        f'{chr(60)}resources{chr(62)}{chr(60)}style name="AppTheme" parent="Theme.AppCompat.DayNight.NoActionBar"{chr(62)}{chr(60)}item name="android:statusBarColor"{chr(62)}#070D18{chr(60)}/item{chr(62)}{chr(60)}/style{chr(62)}{chr(60)}/resources{chr(62)}'
    )
    write(android_dir / "app" / "src" / "main" / "res" / "drawable" / "ic_launcher.xml", (
        f'{chr(60)}vector xmlns:android="http://schemas.android.com/apk/res/android" android:width="108dp" android:height="108dp" android:viewportWidth="108" android:viewportHeight="108"{chr(62)}\n'
        f'    {chr(60)}path android:fillColor="#070D18" android:pathData="M0,0h108v108h-108z"/{chr(62)}\n'
        f'    {chr(60)}path android:fillColor="#00D4AA" android:pathData="M30,30h48v48h-48z"/{chr(62)}\n'
        f"{chr(60)}/vector{chr(62)}\n"
    ))

    # 5. Kotlin Host Classes
    java_dir = android_dir / "app" / "src" / "main" / "java" / pathlib.Path(*pkg.split("."))
    
    write(java_dir / "MainActivity.kt", f"""package {pkg}

import com.facebook.react.ReactActivity
import com.facebook.react.ReactActivityDelegate
import com.facebook.react.defaults.DefaultNewArchitectureEntryPoint.fabricEnabled
import com.facebook.react.defaults.DefaultReactActivityDelegate

class MainActivity : ReactActivity() {{
    override fun getMainComponentName(): String = "{pkg_suffix}"
    override fun createReactActivityDelegate(): ReactActivityDelegate =
        DefaultReactActivityDelegate(this, mainComponentName, fabricEnabled)
}}
""")

    write(java_dir / "MainApplication.kt", f"""package {pkg}

import android.app.Application
import com.facebook.react.PackageList
import com.facebook.react.ReactApplication
import com.facebook.react.ReactHost
import com.facebook.react.ReactNativeHost
import com.facebook.react.ReactPackage
import com.facebook.react.defaults.DefaultNewArchitectureEntryPoint.load
import com.facebook.react.defaults.DefaultReactHost.getDefaultReactHost
import com.facebook.react.defaults.DefaultReactNativeHost
import com.facebook.soloader.SoLoader

class MainApplication : Application(), ReactApplication {{
    override val reactNativeHost: ReactNativeHost =
        object : DefaultReactNativeHost(this) {{
            override fun getPackages(): List<ReactPackage> =
                PackageList(this).packages
            override fun getJSMainModuleName(): String = "index"
            override fun getUseDeveloperSupport(): Boolean = false
            override val isNewArchEnabled: Boolean = false
            override val isHermesEnabled: Boolean = true
        }}

    override val reactHost: ReactHost
        get() = getDefaultReactHost(this.applicationContext, reactNativeHost)

    override fun onCreate() {{
        super.onCreate()
        SoLoader.init(this, false)
    }}
}}
""")

    print(f"[OK] React Native + Hermes Workspace siap untuk {clean_name} ({pkg})")

if __name__ == "__main__":
    main()
