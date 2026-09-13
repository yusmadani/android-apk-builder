#!/usr/bin/env python3
"""
Generate Android native project (Java + XML) dari payload.json.
Bulletproof: auto-fix XML, auto-escape Java literal, manifest bersih,
fallback layout aman, dan validasi Gradle files.
"""
import json
import os
import re
import pathlib
import sys

ROOT = pathlib.Path("project")
PAYLOAD = pathlib.Path("payload.json")


# ---------- Util ----------
def die(msg: str, code: int = 2):
    print(f"[FATAL] {msg}", file=sys.stderr)
    sys.exit(code)


def safe_get(d, key, default=None):
    if not isinstance(d, dict):
        return default
    v = d.get(key, default)
    if v is None:
        return default
    if isinstance(v, str) and v.strip() == "":
        return default
    return v


def sanitize_package(name: str) -> str:
    """Bikin nama package valid dari app_name."""
    if not name:
        name = "MyApp"
    n = re.sub(r"[^A-Za-z0-9_]+", "", name)
    if not n or not re.match(r"[A-Za-z]", n):
        n = "My" + n
    return f"com.example.{n.lower()}"


# ---------- XML helpers ----------
FALLBACK_LAYOUT = """<?xml version="1.0" encoding="utf-8"?>
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:orientation="vertical"
    android:gravity="center"
    android:padding="24dp">

    <TextView
        android:id="@+id/tvTitle"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:text="@string/app_name"
        android:textSize="22sp"
        android:textStyle="bold" />

    <TextView
        android:id="@+id/tvMessage"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:layout_marginTop="12dp"
        android:text="Aplikasi berhasil dibangun."
        android:textSize="16sp" />

</LinearLayout>
"""


def strip_code_fences(s: str) -> str:
    if not isinstance(s, str):
        return ""
    s = s.strip()
    # buang ```xml ... ``` atau ``` ... ```
    s = re.sub(r"^```[a-zA-Z0-9_+-]*\s*", "", s)
    s = re.sub(r"\s*```$", "", s)
    return s.strip()


def fix_xml_escapes(xml: str) -> str:
    """Escape '&' mentah menjadi &amp; tanpa merusak entity yang sudah benar."""
    if not xml:
        return xml
    # Lindungi entity dulu
    placeholders = {}
    def _protect(m):
        key = f"__ENT{len(placeholders)}__"
        placeholders[key] = m.group(0)
        return key
    xml = re.sub(r"&(?:amp|lt|gt|quot|apos|#\d+|#x[0-9a-fA-F]+);", _protect, xml)
    # Sekarang semua & yang tersisa adalah mentah
    xml = xml.replace("&", "&amp;")
    # Kembalikan entity
    for k, v in placeholders.items():
        xml = xml.replace(k, v)
    return xml


def fix_missing_id_prefix(xml: str) -> str:
    """
    - android:id="foo"      -> android:id="@+id/foo"
    - android:id="@id/foo"  -> android:id="@+id/foo"
    - android:id="@android:id/foo" dibiarkan
    """
    def repl(m):
        val = m.group(2)
        if val.startswith("@+id/") or val.startswith("@android:") or val.startswith("@id/android:"):
            return m.group(0)
        if val.startswith("@id/"):
            return f'{m.group(1)}="@+id/{val[len("@id/"):]}"'
        if val.startswith("@"):
            return m.group(0)
        return f'{m.group(1)}="@+id/{val}"'

    return re.sub(r'(android:id)="([^"]*)"', repl, xml)


def ensure_root_xml(xml: str) -> str:
    if not xml:
        return ""
    xml = xml.lstrip("\ufeff \t\r\n")
    if not xml.startswith("<?xml"):
        xml = '<?xml version="1.0" encoding="utf-8"?>\n' + xml
    return xml


def validate_xml(xml: str) -> bool:
    import xml.etree.ElementTree as ET
    try:
        ET.fromstring(xml)
        return True
    except Exception as e:
        print(f"[WARN] XML invalid: {e}", file=sys.stderr)
        return False


def sanitize_layout(raw_xml: str) -> str:
    xml = strip_code_fences(raw_xml)
    xml = ensure_root_xml(xml)
    if not xml or len(xml.strip()) < 30:
        print("[WARN] Layout kosong/terlalu pendek, pakai fallback.", file=sys.stderr)
        return FALLBACK_LAYOUT
    xml = fix_xml_escapes(xml)
    xml = fix_missing_id_prefix(xml)
    if not validate_xml(xml):
        print("[WARN] Layout rusak, pakai fallback.", file=sys.stderr)
        return FALLBACK_LAYOUT
    return xml


# ---------- Java helpers ----------
def sanitize_java_strings(java: str) -> str:
    """
    Perbaiki literal string Java yang rusak akibat newline / escape liar.
    Strategi: cari setiap " ... " pada satu baris logis, escape backslash ganda,
    dan ganti newline literal di dalam string menjadi \\n.
    """
    if not java:
        return java
    java = strip_code_fences(java)

    # 1) Normalisasi CRLF
    java = java.replace("\r\n", "\n").replace("\r", "\n")

    # 2) Ganti backslash yang bukan escape valid menjadi escaped
    #    Valid: \\ \" \' \n \r \t \b \f \0 \uXXXX
    def fix_backslash(m):
        ch = m.group(1)
        if ch in ['\\', '"', "'", 'n', 'r', 't', 'b', 'f', '0']:
            return "\\" + ch
        if ch == 'u':
            return "\\u"
        # karakter lain: escape backslash-nya
        return "\\\\" + ch

    java = re.sub(r"\\(.)", fix_backslash, java, flags=re.DOTALL)

    # 3) Ganti newline literal di dalam string menjadi \n
    #    Kita proses per-karakter untuk menghormati state string.
    out = []
    in_str = False
    i = 0
    n = len(java)
    while i < n:
        c = java[i]
        if in_str:
            if c == '\\' and i + 1 < n:
                out.append(c)
                out.append(java[i+1])
                i += 2
                continue
            if c == '"':
                in_str = False
                out.append(c)
                i += 1
                continue
            if c == '\n':
                out.append('\\n')
                i += 1
                continue
            out.append(c)
            i += 1
        else:
            if c == '"':
                in_str = True
            out.append(c)
            i += 1

    java = "".join(out)
    return java


def ensure_java_package(java: str, pkg: str) -> str:
    if not java:
        return java
    if re.search(r"^\s*package\s+[\w\.]+\s*;", java, flags=re.MULTILINE):
        return java
    return f"package {pkg};\n\n" + java


def ensure_java_imports(java: str) -> str:
    """Tambahkan import yang wajib jika belum ada."""
    needed = {
        "android.os.Bundle": "import android.os.Bundle;",
        "android.app.Activity": "import android.app.Activity;",
    }
    for marker, imp in needed.items():
        if marker.split(".")[-1] not in java:  # sangat kasar
            if imp not in java:
                java = imp + "\n" + java
    return java


def sanitize_java(raw_java: str, pkg: str) -> str:
    java = strip_code_fences(raw_java)
    if not java or "class " not in java:
        print("[WARN] Java kosong/tidak valid, pakai MainActivity fallback.", file=sys.stderr)
        java = (
            "package {pkg};\n\n"
            "import android.app.Activity;\n"
            "import android.os.Bundle;\n\n"
            "public class MainActivity extends Activity {{\n"
            "    @Override\n"
            "    protected void onCreate(Bundle savedInstanceState) {{\n"
            "        super.onCreate(savedInstanceState);\n"
            "        setContentView(R.layout.activity_main);\n"
            "    }}\n"
            "}}\n"
        ).format(pkg=pkg)
        return java

    java = sanitize_java_strings(java)
    java = ensure_java_package(java, pkg)

    # Pastikan extends Activity (hindari crash MaterialComponents)
    java = re.sub(r"extends\s+AppCompatActivity", "extends Activity", java)
    java = re.sub(r"import\s+androidx\.appcompat\.app\.AppCompatActivity;", "", java)
    java = ensure_java_imports(java)
    return java


# ---------- Writes ----------
def write(path: pathlib.Path, content: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def main():
    if not PAYLOAD.exists():
        die("payload.json tidak ditemukan")
    try:
        data = json.loads(PAYLOAD.read_text(encoding="utf-8"))
    except Exception as e:
        die(f"payload.json bukan JSON valid: {e}")

    app_name = safe_get(data, "app_name", "MyApp")
    layout_raw = safe_get(data, "activity_main_xml", "")
    java_raw = safe_get(data, "main_activity_java", "")

    pkg = sanitize_package(app_name)
    layout_xml = sanitize_layout(layout_raw)
    main_java = sanitize_java(java_raw, pkg)

    # -------- Root project --------
    write(ROOT / "settings.gradle", (
        "pluginManagement {\n"
        "    repositories {\n"
        "        google()\n"
        "        mavenCentral()\n"
        "        gradlePluginPortal()\n"
        "    }\n"
        "}\n"
        "dependencyResolutionManagement {\n"
        "    repositoriesMode.set(RepositoriesMode.PREFER_SETTINGS)\n"
        "    repositories {\n"
        "        google()\n"
        "        mavenCentral()\n"
        "    }\n"
        "}\n"
        "rootProject.name = \"App\"\n"
        "include ':app'\n"
    ))

    write(ROOT / "build.gradle", (
        "plugins {\n"
        "    id 'com.android.application' version '8.5.2' apply false\n"
        "}\n"
    ))

    write(ROOT / "gradle.properties", (
        "org.gradle.jvmargs=-Xmx2048m -Dfile.encoding=UTF-8\n"
        "android.useAndroidX=true\n"
        "android.nonTransitiveRClass=true\n"
    ))

    # -------- app module --------
    write(ROOT / "app" / "build.gradle", (
        "plugins { id 'com.android.application' }\n\n"
        "android {\n"
        "    namespace '" + pkg + "'\n"
        "    compileSdk 34\n\n"
        "    defaultConfig {\n"
        "        applicationId '" + pkg + "'\n"
        "        minSdk 21\n"
        "        targetSdk 34\n"
        "        versionCode 1\n"
        "        versionName '1.0'\n"
        "    }\n\n"
        "    buildTypes {\n"
        "        release { minifyEnabled false }\n"
        "    }\n\n"
        "    compileOptions {\n"
        "        sourceCompatibility JavaVersion.VERSION_17\n"
        "        targetCompatibility JavaVersion.VERSION_17\n"
        "    }\n"
        "}\n\n"
        "dependencies {\n"
        "    implementation 'androidx.annotation:annotation:1.9.1'\n"
        "}\n"
    ))

    # Manifest — dipastikan baris pertama tanpa indentasi apapun
    manifest = (
        '<?xml version="1.0" encoding="utf-8"?>\n'
        '<manifest xmlns:android="http://schemas.android.com/apk/res/android">\n'
        '    <application\n'
        '        android:allowBackup="true"\n'
        '        android:label="@string/app_name"\n'
        '        android:supportsRtl="true"\n'
        '        android:theme="@android:style/Theme.DeviceDefault.NoActionBar">\n'
        '        <activity\n'
        '            android:name=".MainActivity"\n'
        '            android:exported="true">\n'
        '            <intent-filter>\n'
        '                <action android:name="android.intent.action.MAIN" />\n'
        '                <category android:name="android.intent.category.LAUNCHER" />\n'
        '            </intent-filter>\n'
        '        </activity>\n'
        '    </application>\n'
        '</manifest>\n'
    )
    write(ROOT / "app" / "src" / "main" / "AndroidManifest.xml", manifest)

    # resources
    write(ROOT / "app" / "src" / "main" / "res" / "values" / "strings.xml", (
        '<?xml version="1.0" encoding="utf-8"?>\n'
        '<resources>\n'
        f'    <string name="app_name">{app_name}</string>\n'
        '</resources>\n'
    ))

    write(ROOT / "app" / "src" / "main" / "res" / "values" / "colors.xml", (
        '<?xml version="1.0" encoding="utf-8"?>\n'
        '<resources>\n'
        '    <color name="black">#FF000000</color>\n'
        '    <color name="white">#FFFFFFFF</color>\n'
        '</resources>\n'
    ))

    write(ROOT / "app" / "src" / "main" / "res" / "layout" / "activity_main.xml", layout_xml)

    java_path = ROOT / "app" / "src" / "main" / "java" / pathlib.Path(*pkg.split("."))
    write(java_path / "MainActivity.java", main_java)

    # Gradle wrapper (di-generate langsung, tanpa download)
    write(ROOT / "gradlew", GRADLEW_SH)
    os.chmod(ROOT / "gradlew", 0o755)
    write(ROOT / "gradlew.bat", GRADLEW_BAT)

    write(ROOT / "gradle" / "wrapper" / "gradle-wrapper.properties", (
        "distributionBase=GRADLE_USER_HOME\n"
        "distributionPath=wrapper/dists\n"
        "distributionUrl=https\\://services.gradle.org/distributions/gradle-8.7-bin.zip\n"
        "zipStoreBase=GRADLE_USER_HOME\n"
        "zipStorePath=wrapper/dists\n"
    ))

    print("[OK] Project generated at:", ROOT.resolve())
    print("[OK] package =", pkg)
    print("[OK] layout bytes =", len(layout_xml))
    print("[OK] java bytes =", len(main_java))


# ---------- Gradle wrapper scripts (embedded) ----------
GRADLEW_SH = r"""#!/bin/sh
# Minimal gradle wrapper launcher
set -e
APP_HOME=$(cd "$(dirname "$0")" && pwd)
CLASSPATH=$APP_HOME/gradle/wrapper/gradle-wrapper.jar
if [ ! -f "$CLASSPATH" ]; then
  # fallback: pakai gradle dari sistem jika ada
  if command -v gradle >/dev/null 2>&1; then
    exec gradle "$@"
  fi
  # download wrapper jar
  mkdir -p "$APP_HOME/gradle/wrapper"
  URL="https://raw.githubusercontent.com/gradle/gradle/v8.7.0/gradle/wrapper/gradle-wrapper.jar"
  if command -v curl >/dev/null 2>&1; then
    curl -fsSL -o "$CLASSPATH" "$URL"
  elif command -v wget >/dev/null 2>&1; then
    wget -q -O "$CLASSPATH" "$URL"
  fi
fi
exec java -classpath "$CLASSPATH" org.gradle.wrapper.GradleWrapperMain "$@"
"""

GRADLEW_BAT = r"""@echo off
set DIRNAME=%~dp0
if "%DIRNAME%"=="" set DIRNAME=.
java -classpath "%DIRNAME%gradle\wrapper\gradle-wrapper.jar" org.gradle.wrapper.GradleWrapperMain %*
"""


if __name__ == "__main__":
    main()
