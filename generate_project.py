#!/usr/bin/env python3
"""
Industrial Dynamic Android Engine (Universal Studio Edition)
- Syntax Error Fixed: String JS dan Python terisolasi sempurna.
- Dynamic Multi-App: Mendukung Kasir, Gym, Jadwal, Habit, dll.
- Pre-baked Material Components & AndroidX WebViewAssetLoader.
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

PRO_STUDIO_CSS = """
:root {
  --bg-deep: #070B14;
  --bg-card: rgba(18, 26, 43, 0.85);
  --bg-card-border: rgba(99, 102, 241, 0.22);
  --primary-neon: #00F0FF;
  --secondary-neon: #7000FF;
  --accent-emerald: #10B981;
  --accent-rose: #F43F5E;
  --text-pure: #FFFFFF;
  --text-muted: #94A3B8;
  --safe-bottom: env(safe-area-inset-bottom, 22px);
}
* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
  -webkit-tap-highlight-color: transparent;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  user-select: none;
}
body {
  background: radial-gradient(circle at top right, #111827, #070B14 80%);
  color: var(--text-pure);
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  overflow-x: hidden;
  padding-bottom: calc(75px + var(--safe-bottom));
}
.app-header {
  position: sticky;
  top: 0;
  z-index: 90;
  background: rgba(7, 11, 20, 0.85);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border-bottom: 1px solid var(--bg-card-border);
  padding: 16px 20px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.app-header h1 {
  font-size: 1.25rem;
  font-weight: 800;
  letter-spacing: -0.02em;
  background: linear-gradient(135deg, var(--primary-neon), #818CF8);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}
.container {
  padding: 18px;
  display: flex;
  flex-direction: column;
  gap: 16px;
  flex: 1;
}
.view {
  display: none;
  animation: fadeIn 0.25s cubic-bezier(0.16, 1, 0.3, 1);
}
.view.active {
  display: block;
}
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(6px); }
  to { opacity: 1; transform: translateY(0); }
}
.glass-card {
  background: var(--bg-card);
  border: 1px solid var(--bg-card-border);
  border-radius: 18px;
  padding: 18px;
  box-shadow: 0 10px 30px -10px rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(12px);
  margin-bottom: 14px;
}
.stat-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 10px;
  margin-bottom: 14px;
}
.stat-box {
  background: rgba(15, 23, 42, 0.6);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 14px;
  padding: 12px 8px;
  text-align: center;
}
.stat-val { font-size: 1.35rem; font-weight: 800; color: var(--primary-neon); }
.stat-lbl { font-size: 0.68rem; color: var(--text-muted); text-transform: uppercase; margin-top: 2px; }
.progress-bar-bg {
  width: 100%;
  height: 8px;
  background: rgba(255, 255, 255, 0.08);
  border-radius: 999px;
  overflow: hidden;
  margin: 10px 0;
}
.progress-bar-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--primary-neon), var(--accent-emerald));
  width: 0%;
  transition: width 0.4s ease;
}
.exercise-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 16px;
  background: rgba(15, 23, 42, 0.7);
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 14px;
  margin-bottom: 10px;
  transition: all 0.2s ease;
}
.exercise-row.completed {
  border-color: rgba(16, 185, 129, 0.4);
  background: rgba(16, 185, 129, 0.08);
}
.exercise-row.completed .exercise-title {
  text-decoration: line-through;
  opacity: 0.6;
}
.btn-action {
  background: linear-gradient(135deg, var(--primary-neon), #3B82F6);
  color: #050811;
  font-weight: 700;
  font-size: 0.95rem;
  border: none;
  padding: 14px 20px;
  border-radius: 14px;
  width: 100%;
  cursor: pointer;
  box-shadow: 0 4px 20px rgba(0, 240, 255, 0.3);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}
.btn-action:active { transform: scale(0.98); }
.btn-danger { background: var(--accent-rose); color: white; box-shadow: 0 4px 20px rgba(244, 63, 94, 0.3); }
.tab-bar {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  height: calc(64px + var(--safe-bottom));
  padding-bottom: var(--safe-bottom);
  background: rgba(7, 11, 20, 0.95);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border-top: 1px solid rgba(255, 255, 255, 0.08);
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
  font-size: 0.75rem;
  font-weight: 600;
  gap: 4px;
  cursor: pointer;
  flex: 1;
  height: 100%;
}
.tab-item.active {
  color: var(--primary-neon);
}
.tab-item .icon { font-size: 1.3rem; }
"""

PRO_STUDIO_JS = """
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
    if (window.Android && window.Android.vibrate) { window.Android.vibrate(ms || 35); }
  }
};
window.switchTab = function(targetId) {
  if (!targetId) return;
  targetId = targetId.replace('#', '');
  document.querySelectorAll('.view, section[id]').forEach(function(v) {
    v.style.display = 'none';
    v.classList.remove('active');
  });
  var target = document.getElementById(targetId) || document.getElementById('tab-' + targetId);
  if (!target) target = document.getElementById(targetId.replace('tab-', ''));
  if (target) {
    target.style.display = 'block';
    target.classList.add('active');
  }
  document.querySelectorAll('.tab-item').forEach(function(btn) {
    var raw = (btn.getAttribute('data-tab') || btn.getAttribute('onclick') || '').toLowerCase();
    if (raw.indexOf(targetId.toLowerCase()) !== -1) {
      btn.classList.add('active');
    } else {
      btn.classList.remove('active');
    }
  });
  Native.vibrate(25);
};
document.addEventListener('click', function(e) {
  var tabBtn = e.target.closest('.tab-item');
  if (tabBtn) {
    var target = tabBtn.getAttribute('data-tab');
    if (!target) {
      var oc = tabBtn.getAttribute('onclick') || '';
      var m = oc.match(/switchTab\\(['"]([^'"]+)['"]\\)/);
      if (m) target = m[1];
    }
    if (target) {
      e.preventDefault();
      switchTab(target);
    }
  }
});
"""

DEFAULT_FALLBACK_UI = """
<!-- VIEW 1: DASHBOARD -->
<section id="tab-dashboard" class="view active">
  <div class="glass-card">
    <div style="display:flex; justify-content:space-between; align-items:center;">
      <div>
        <h2 style="font-size:1.1rem; font-weight:700;">Progress Hari Ini</h2>
        <p style="font-size:0.8rem; color:var(--text-muted);">Target Latihan Otot & Kardio</p>
      </div>
      <span id="progress-text" style="font-size:1.2rem; font-weight:800; color:var(--primary-neon);">0%</span>
    </div>
    <div class="progress-bar-bg">
      <div id="progress-bar" class="progress-bar-fill"></div>
    </div>
    <div class="stat-grid">
      <div class="stat-box"><div id="stat-total" class="stat-val">5</div><div class="stat-lbl">Gerakan</div></div>
      <div class="stat-box"><div id="stat-done" class="stat-val">0</div><div class="stat-lbl">Selesai</div></div>
      <div class="stat-box"><div id="stat-cal" class="stat-val">0</div><div class="stat-lbl">Kkal</div></div>
    </div>
  </div>

  <div class="glass-card" style="text-align:center;">
    <span style="font-size:0.75rem; text-transform:uppercase; color:var(--text-muted); letter-spacing:0.05em;">Timer Istirahat Set</span>
    <div id="timer-display" style="font-size:2.8rem; font-weight:900; color:var(--primary-neon); margin:4px 0;">00:60</div>
    <div style="display:flex; gap:10px;">
      <button class="btn-action" style="flex:1;" onclick="startRestTimer(60)">⏱️ Mulai 60s</button>
      <button class="btn-action btn-danger" style="width:70px;" onclick="resetTimer()">Reset</button>
    </div>
  </div>
</section>

<!-- VIEW 2: LATIHAN -->
<section id="tab-latihan" class="view">
  <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
    <h2 style="font-size:1.15rem; font-weight:800; color:var(--primary-neon);">Daftar Latihan</h2>
    <button onclick="resetAllExercises()" style="background:none; border:none; color:var(--accent-rose); font-size:0.8rem; font-weight:600;">Reset Harian</button>
  </div>
  <div id="exercise-list"></div>
</section>

<!-- VIEW 3: RIWAYAT -->
<section id="tab-riwayat" class="view">
  <div class="glass-card">
    <h3 style="font-size:1.05rem; margin-bottom:10px;">📊 Catatan Beban Maksimal</h3>
    <p style="font-size:0.85rem; color:var(--text-muted); line-height:1.5;">
      • Dumbbell Bench Press: <b>24 Kg</b><br>
      • Lat Pulley Pulldown: <b>55 Kg</b><br>
      • Incline Dumbbell Curl: <b>14 Kg</b><br>
      • Triceps Cable Pushdown: <b>40 Kg</b>
    </p>
  </div>
  <div class="glass-card" style="text-align:center;">
    <button class="btn-action btn-danger" onclick="clearAllData()">🗑️ Kosongkan Seluruh Data</button>
  </div>
</section>

<nav class="tab-bar">
  <button class="tab-item active" data-tab="tab-dashboard"><span class="icon">🏠</span>Dashboard</button>
  <button class="tab-item" data-tab="tab-latihan"><span class="icon">🏋️</span>Latihan</button>
  <button class="tab-item" data-tab="tab-riwayat"><span class="icon">📊</span>Riwayat</button>
</nav>

<script>
var DEFAULT_EXERCISES = [
  { id: 1, name: "Dumbbell Bench Press", target: "Dada", sets: "4 Set x 12 Reps", weight: "20 Kg", done: false },
  { id: 2, name: "Lat Pulley Pulldown", target: "Punggung", sets: "4 Set x 10 Reps", weight: "50 Kg", done: false },
  { id: 3, name: "Dumbbell Shoulder Press", target: "Bahu", sets: "3 Set x 12 Reps", weight: "16 Kg", done: false },
  { id: 4, name: "Cable Pulley Triceps", target: "Triceps", sets: "3 Set x 15 Reps", weight: "35 Kg", done: false },
  { id: 5, name: "Dumbbell Biceps Curl", target: "Biceps", sets: "4 Set x 12 Reps", weight: "12 Kg", done: false }
];

var exercises = DB.get('gym_exercises', DEFAULT_EXERCISES);
var timerInterval = null;
var timerSeconds = 60;

function renderExercises() {
  var container = document.getElementById('exercise-list');
  if (!container) return;
  container.innerHTML = '';
  var doneCount = 0;

  exercises.forEach(function(item) {
    if (item.done) doneCount++;
    var row = document.createElement('div');
    row.className = 'exercise-row' + (item.done ? ' completed' : '');
    row.innerHTML = '<div>' +
      '<div class="exercise-title" style="font-weight:700; font-size:0.95rem;">' + item.name + '</div>' +
      '<div style="font-size:0.75rem; color:var(--text-muted); margin-top:2px;">' + item.target + ' • ' + item.sets + ' (' + item.weight + ')</div>' +
      '</div>' +
      '<button onclick="toggleDone(' + item.id + ')" style="padding:8px 14px; border-radius:10px; border:none; font-weight:700; font-size:0.78rem; cursor:pointer; background:' + (item.done ? 'var(--accent-emerald)' : 'rgba(255,255,255,0.1)') + '; color:' + (item.done ? '#000' : '#fff') + ';">' + (item.done ? '✓ SELESAI' : 'CHECK') + '</button>';
    container.appendChild(row);
  });

  var pct = exercises.length > 0 ? Math.round((doneCount / exercises.length) * 100) : 0;
  var pBar = document.getElementById('progress-bar');
  var pTxt = document.getElementById('progress-text');
  var sDone = document.getElementById('stat-done');
  var sCal = document.getElementById('stat-cal');
  var sTotal = document.getElementById('stat-total');

  if (pBar) pBar.style.width = pct + '%';
  if (pTxt) pTxt.innerText = pct + '%';
  if (sDone) sDone.innerText = doneCount;
  if (sTotal) sTotal.innerText = exercises.length;
  if (sCal) sCal.innerText = doneCount * 65;
}

window.toggleDone = function(id) {
  exercises = exercises.map(function(e) {
    if (e.id === id) e.done = !e.done;
    return e;
  });
  DB.set('gym_exercises', exercises);
  Native.vibrate(35);
  renderExercises();
  if (exercises.find(function(e){ return e.id === id; }).done) {
    Native.toast('Gerakan selesai! Istirahat 60 detik.');
    startRestTimer(60);
  }
};

window.startRestTimer = function(sec) {
  clearInterval(timerInterval);
  timerSeconds = sec;
  var d = document.getElementById('timer-display');
  timerInterval = setInterval(function() {
    timerSeconds--;
    var m = Math.floor(timerSeconds / 60);
    var s = timerSeconds % 60;
    if (d) d.innerText = (m < 10 ? '0' : '') + m + ':' + (s < 10 ? '0' : '') + s;
    if (timerSeconds <= 0) {
      clearInterval(timerInterval);
      Native.vibrate(80);
      Native.toast('Waktu istirahat selesai! Lanjut set berikutnya.');
    }
  }, 1000);
};

window.resetTimer = function() {
  clearInterval(timerInterval);
  var d = document.getElementById('timer-display');
  if (d) d.innerText = "00:60";
};

window.resetAllExercises = function() {
  exercises = exercises.map(function(e){ e.done = false; return e; });
  DB.set('gym_exercises', exercises);
  Native.toast('Progress harian direset.');
  renderExercises();
};

window.clearAllData = function() {
  localStorage.clear();
  exercises = DEFAULT_EXERCISES;
  Native.toast('Seluruh database dikosongkan.');
  renderExercises();
};

document.addEventListener('DOMContentLoaded', function() {
  renderExercises();
  setTimeout(function() { switchTab('tab-dashboard'); }, 100);
});
</script>
"""

def assemble_pro_html(user_html, app_title):
    if not user_html or len(user_html.strip()) < 120 or "<section" not in user_html:
        body_content = DEFAULT_FALLBACK_UI
    else:
        body_content = user_html

    return (
        "<!DOCTYPE html>\n<html lang=\"id\">\n<head>\n"
        "  <meta charset=\"UTF-8\">\n"
        "  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no\">\n"
        "  <title>" + app_title + "</title>\n"
        "  <style>" + PRO_STUDIO_CSS + "</style>\n"
        "  <script>" + PRO_STUDIO_JS + "</script>\n"
        "</head>\n<body>\n"
        "  <header class=\"app-header\">\n"
        "    <h1>" + app_title + "</h1>\n"
        "    <span style=\"font-size:1.2rem;\">⚡</span>\n"
        "  </header>\n"
        "  <div class=\"container\">\n"
        + body_content +
        "\n  </div>\n</body>\n</html>"
    )

def main():
    raw_name = "JadwalGym"
    b64 = None

    if len(sys.argv) >= 3:
        raw_name = sys.argv[1]
        b64 = sys.argv[2]
    elif PAYLOAD.exists():
        try:
            data = json.loads(PAYLOAD.read_text(encoding="utf-8"))
            raw_name = data.get("app_name", "JadwalGym")
            b64 = data.get("html_code_b64") or data.get("xml_code_b64") or data.get("code_b64")
        except Exception:
            pass

    clean_name = re.sub(r"[^\w\s-]", "", raw_name).strip() or "JadwalGym"
    pkg_suffix = re.sub(r"[^a-zA-Z0-9]", "", clean_name).lower() or "jadwalgym"
    pkg = f"com.centoa.{pkg_suffix}"

    raw_html = ""
    if b64:
        try:
            raw_html = base64.b64decode(b64).decode("utf-8", errors="ignore")
        except Exception:
            raw_html = ""

    final_html = assemble_pro_html(raw_html, clean_name)

    def write(p, content):
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")

    # 1. Gradle Setup
    write(ROOT / "gradle" / "wrapper" / "gradle-wrapper.properties",
        "distributionBase=GRADLE_USER_HOME\n"
        "distributionPath=wrapper/dists\n"
        "distributionUrl=https\\://services.gradle.org/distributions/gradle-8.7-bin.zip\n"
        "zipStoreBase=GRADLE_USER_HOME\n"
        "zipStorePath=wrapper/dists\n"
    )

    write(ROOT / "settings.gradle",
        "pluginManagement { repositories { google(); mavenCentral(); gradlePluginPortal() } }\n"
        "dependencyResolutionManagement { repositoriesMode.set(RepositoriesMode.PREFER_SETTINGS); repositories { google(); mavenCentral() } }\n"
        f"rootProject.name = '{pkg_suffix}'\n"
        "include ':app'\n"
    )

    write(ROOT / "build.gradle",
        "plugins { id 'com.android.application' version '8.5.2' apply false }\n"
    )

    write(ROOT / "gradle.properties",
        "org.gradle.jvmargs=-Xmx2048m -Dfile.encoding=UTF-8\n"
        "android.useAndroidX=true\n"
        "android.nonTransitiveRClass=true\n"
    )

    write(ROOT / "app" / "build.gradle",
        "plugins { id 'com.android.application' }\n\n"
        "android {\n"
        f"    namespace '{pkg}'\n"
        "    compileSdk 34\n\n"
        "    defaultConfig {\n"
        f"        applicationId '{pkg}'\n"
        "        minSdk 21\n"
        "        targetSdk 34\n"
        "        versionCode 1\n"
        "        versionName '1.5'\n"
        "    }\n"
        "    buildTypes {\n"
        "        release {\n"
        "            minifyEnabled false\n"
        "        }\n"
        "    }\n"
        "    compileOptions {\n"
        "        sourceCompatibility JavaVersion.VERSION_17\n"
        "        targetCompatibility JavaVersion.VERSION_17\n"
        "    }\n"
        "}\n"
        "dependencies {\n"
        "    implementation 'androidx.appcompat:appcompat:1.6.1'\n"
        "    implementation 'com.google.android.material:material:1.11.0'\n"
        "    implementation 'androidx.webkit:webkit:1.10.0'\n"
        "}\n"
    )

    # 2. Manifest & Aset
    write(ROOT / "app" / "src" / "main" / "AndroidManifest.xml",
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
        f'        android:theme="@style/Theme.Design.NoActionBar"{GT}\n'
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
    )

    write(ROOT / "app" / "src" / "main" / "res" / "values" / "strings.xml",
        f'{LT}resources{GT}{LT}string name="app_name"{GT}{clean_name}{LT}/string{GT}{LT}/resources{GT}'
    )
    write(ROOT / "app" / "src" / "main" / "res" / "values" / "styles.xml",
        f'{LT}resources{GT}{LT}style name="Theme.Design.NoActionBar" parent="Theme.MaterialComponents.DayNight.NoActionBar"{GT}{LT}item name="android:statusBarColor"{GT}#070B14{LT}/item{GT}{LT}item name="android:navigationBarColor"{GT}#070B14{LT}/item{GT}{LT}/style{GT}{LT}/resources{GT}'
    )
    write(ROOT / "app" / "src" / "main" / "res" / "drawable" / "ic_launcher.xml",
        f"{LT}?xml version=\"1.0\" encoding=\"utf-8\"?{GT}\n"
        f'{LT}vector xmlns:android="http://schemas.android.com/apk/res/android" android:width="108dp" android:height="108dp" android:viewportWidth="108" android:viewportHeight="108"{GT}\n'
        f'    {LT}path android:fillColor="#070B14" android:pathData="M0,0h108v108h-108z"/{GT}\n'
        f'    {LT}path android:fillColor="#00F0FF" android:pathData="M54,20L74,40H60V74H48V40H34L54,20Z"/{GT}\n'
        f"{LT}/vector{GT}\n"
    )
    write(ROOT / "app" / "src" / "main" / "assets" / "index.html", final_html)

    # 3. MainActivity
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
        "            window.setStatusBarColor(Color.parseColor(\"#070B14\"));\n"
        "            window.setNavigationBarColor(Color.parseColor(\"#070B14\"));\n"
        "        }\n\n"
        "        webView = new WebView(this);\n"
        "        webView.setBackgroundColor(Color.parseColor(\"#070B14\"));\n"
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
    print(f"[OK] Studio Engine siap untuk {clean_name} ({pkg})")

if __name__ == "__main__":
    main()
