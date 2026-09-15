#!/usr/bin/env python3
"""
Generate Android native project (Java + XML) dari payload.json.
Lengkap: Debug log payload, Package ID unik per aplikasi,
multi-key JSON reader, dan proteksi anti-HTML stripping.
"""
import json
import os
import pathlib
import re
import sys
import xml.etree.ElementTree as ET

ROOT = pathlib.Path(".")
PAYLOAD = pathlib.Path("payload.json")

LT = chr(60)  # Simbol '<'
GT = chr(62)  # Simbol '>'


def die(msg, code=2):
    print(f"[FATAL] {msg}", file=sys.stderr)
    sys.exit(code)


def safe_get(d, keys, default=""):
    """Membaca berbagai kemungkinan nama key dari payload bot."""
    if not isinstance(d, dict):
        return default
    if isinstance(keys, str):
        keys = [keys]
    for k in keys:
        v = d.get(k)
        if v and isinstance(v, str) and v.strip():
            return v.strip()
    return default


# Template Layout Darurat jika kode dari AI benar-benar kosong
FALLBACK_LAYOUT = (
    LT + '?xml version="1.0" encoding="utf-8"?' + GT + '\n'
    + LT + 'LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"\n'
    + '    android:layout_width="match_parent"\n'
    + '    android:layout_height="match_parent"\n'
    + '    android:orientation="vertical"\n'
    + '    android:gravity="center"\n'
    + '    android:padding="24dp">\n\n'
    + '    ' + LT + 'TextView\n'
    + '        android:id="@+id/tvTitle"\n'
    + '        android:layout_width="wrap_content"\n'
    + '        android:layout_height="wrap_content"\n'
    + '        android:text="@string/app_name"\n'
    + '        android:textSize="22sp"\n'
    + '        android:textStyle="bold" /' + GT + '\n\n'
    + '    ' + LT + 'TextView\n'
    + '        android:id="@+id/tvMessage"\n'
    + '        android:layout_width="wrap_content"\n'
    + '        android:layout_height="wrap_content"\n'
    + '        android:layout_marginTop="12dp"\n'
    + '        android:text="Aplikasi berhasil dibangun."\n'
    + '        android:textSize="16sp" /' + GT + '\n\n'
    + LT + '/LinearLayout' + GT + '\n'
)

COLORS_XML = (
    LT + '?xml version="1.0" encoding="utf-8"?' + GT + '\n'
    + LT + 'resources' + GT + '\n'
    + '    ' + LT + 'color name="black"' + GT + '#FF000000' + LT + '/color' + GT + '\n'
    + '    ' + LT + 'color name="white"' + GT + '#FFFFFFFF' + LT + '/color' + GT + '\n'
    + LT + '/resources' + GT + '\n'
)

IC_LAUNCHER_XML = (
    LT + '?xml version="1.0" encoding="utf-8"?' + GT + '\n'
    + LT + 'vector xmlns:android="http://schemas.android.com/apk/res/android"\n'
    + '    android:width="108dp"\n'
    + '    android:height="108dp"\n'
    + '    android:viewportWidth="108"\n'
    + '    android:viewportHeight="108"' + GT + '\n'
    + '    ' + LT + 'path\n'
    + '        android:fillColor="#008577"\n'
    + '        android:pathData="M0,0h108v108h-108z"/' + GT + '\n'
    + '    ' + LT + 'path\n'
    + '        android:fillColor="#FFFFFF"\n'
    + '        android:pathData="M54,20L74,40H60V74H48V40H34L54,20Z"/' + GT + '\n'
    + LT + '/vector' + GT + '\n'
)


def strip_code_fences(s):
    if not isinstance(s, str):
        return ""
    s = s.strip()
    s = re.sub(r"^```[a-zA-Z0-9_+-]*\s*", "", s)
    s = re.sub(r"\s*```$", "", s)
    return s.strip()


def fix_xml_escapes(xml):
    if not xml:
        return xml
    placeholders = {}

    def _protect(m):
        key = f"__ENT{len(placeholders)}__"
        placeholders[key] = m.group(0)
        return key

    xml = re.sub(r"&(?:amp|lt|gt|quot|apos|#\d+|#x[0-9a-fA-F]+);", _protect, xml)
    xml = xml.replace("&", "&")
    for k, v in placeholders.items():
        xml = xml.replace(k, v)
    return xml


def fix_missing_id_prefix(xml):
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


def ensure_root_xml(xml):
    if not xml:
        return ""
    xml = xml.lstrip("\ufeff \t\r\n")
    header = LT + '?xml version="1.0" encoding="utf-8"?' + GT + '\n'
    if not xml.startswith(LT + "?xml"):
        xml = header + xml
    return xml


def validate_xml(xml):
    try:
        ET.fromstring(xml)
        return True
    except Exception as e:
        print(f"[WARN] Validasi XML gagal: {e}", file=sys.stderr)
        return False


def sanitize_layout(raw_xml):
    xml = strip_code_fences(raw_xml)
    xml = ensure_root_xml(xml)
    if not xml or len(xml.strip()) in range(0, 30):
        print("[WARN] Kode Layout kosong/hilang! Memakai fallback template.", file=sys.stderr)
        return FALLBACK_LAYOUT
    xml = fix_xml_escapes(xml)
    xml = fix_missing_id_prefix(xml)
    if not validate_xml(xml):
        print("[WARN] Format XML rusak! Memakai fallback template.", file=sys.stderr)
        return FALLBACK_LAYOUT
    return xml


def sanitize_java_strings(java):
    if not java:
        return java
    java = strip_code_fences(java)
    java = java.replace("\r\n", "\n").replace("\r", "\n")
    java = re.sub(r'"\s*\n\s*', '" + "', java)

    out = []
    in_str = False
    i = 0
    n = len(java)
    while i != n:
        c = java[i]
        if in_str:
            if c == '\\' and i + 1 != n:
                out.append(c)
                out.append(java[i + 1])
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

    return "".join(out)


def sanitize_java(raw_java, pkg):
    java = strip_code_fences(raw_java)
    if not java or "class " not in java:
        print("[WARN] Kode Java kosong/hilang! Memakai MainActivity fallback.", file=sys.stderr)
        return (
            f"package {pkg};\n\n"
            "import android.app.Activity;\n"
            "import android.os.Bundle;\n\n"
            "public class MainActivity extends Activity {\n"
            "    @Override\n"
            "    protected void onCreate(Bundle savedInstanceState) {\n"
            "        super.onCreate(savedInstanceState);\n"
            "        setContentView(R.layout.activity_main);\n"
            "    }\n"
            "}\n"
        )

    java = sanitize_java_strings(java)

    if re.search(r"package\s+[\w\.]+;", java):
        java = re.sub(r"package\s+[\w\.]+;", f"package {pkg};", java)
    else:
        java = f"package {pkg};\n\n" + java

    java = re.sub(r"extends\s+AppCompatActivity", "extends Activity", java)
    java = re.sub(r"import\s+androidx\.appcompat\.app\.AppCompatActivity;", "", java)

    essential_imports = [
        "import android.app.Activity;",
        "import android.os.Bundle;",
        "import android.view.View;",
        "import android.widget.*;",
    ]
    for imp in essential_imports:
        if imp not in java:
            java = re.sub(r"(package\s+[\w\.]+;\n*)", r"\1" + imp + "\n", java)

    return java


def write(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def main():
    if not PAYLOAD.exists():
        die("payload.json tidak ditemukan!")
    try:
        data = json.loads(PAYLOAD.read_text(encoding="utf-8"))
    except Exception as e:
        die(f"payload.json bukan format JSON valid: {e}")

    # ========================================================
    # LOG DEBUG: Memeriksa isi asli data yang dikirim dari STB
    # ========================================================
    print("==================================================")
    print("=== ISI PAYLOAD.JSON YANG DITERIMA DARI STB ===")
    print("Daftar Kunci (Keys):", list(data.keys()))
    for k, v in data.items():
        if isinstance(v, str):
            cuplikan = repr(v[:60]) + ("..." if len(v) > 60 else "")
            print(f"-> Key '{k}': {len(v)} karakter | {cuplikan}")
        else:
            print(f"-> Key '{k}': {repr(v)}")
    print("==================================================")
    # ========================================================

    # 1. Bersihkan Nama Aplikasi
    raw_name = safe_get(data, ["app_name", "title", "name"], "DynamicApp")
    clean_app_name = re.sub(LT + r"[^" + GT + r"]+" + GT, "", raw_name)
    clean_app_name = (
        clean_app_name.replace("&", "&")
        .replace("'", "\\'")
        .replace('"', '\\"')
        .strip()
    )
    if not clean_app_name:
        clean_app_name = "DynamicApp"

    # 2. Package Name Dinamis (Anti-Bentrok saat dipasang di HP)
    pkg_suffix = re.sub(r"[^a-zA-Z0-9]", "", clean_app_name).lower()
    if not pkg_suffix or len(pkg_suffix) < 3:
        pkg_suffix = "dynamicapp"
    pkg = f"com.stb.{pkg_suffix}"

    # 3. Baca Kode Layout & Java (Mendukung Multi-Key)
    layout_raw = safe_get(data, ["activity_main_xml", "layout_xml", "layout", "xml", "code_xml"])
    java_raw = safe_get(data, ["main_activity_java", "java_code", "main_activity", "java", "code"])

    print(f"[*] App Name        : {clean_app_name}")
    print(f"[*] Dynamic Package : {pkg}")
    print(f"[*] Input XML size  : {len(layout_raw)} bytes")
    print(f"[*] Input Java size : {len(java_raw)} bytes")

    layout_xml = sanitize_layout(layout_raw)
    main_java = sanitize_java(java_raw, pkg)

    # 4. Konfigurasi Gradle
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
        f"rootProject.name = '{pkg_suffix}'\n"
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

    # 5. Manifest
    manifest_content = (
        LT + '?xml version="1.0" encoding="utf-8"?' + GT + '\n'
        + LT + 'manifest xmlns:android="http://schemas.android.com/apk/res/android">\n'
        + '    ' + LT + 'application\n'
        + '        android:allowBackup="true"\n'
        + '        android:icon="@drawable/ic_launcher"\n'
        + '        android:label="@string/app_name"\n'
        + '        android:supportsRtl="true"\n'
        + '        android:theme="@android:style/Theme.DeviceDefault.NoActionBar">\n'
        + '        ' + LT + 'activity\n'
        + '            android:name=".MainActivity"\n'
        + '            android:exported="true">\n'
        + '            ' + LT + 'intent-filter>\n'
        + '                ' + LT + 'action android:name="android.intent.action.MAIN" /' + GT + '\n'
        + '                ' + LT + 'category android:name="android.intent.category.LAUNCHER" /' + GT + '\n'
        + '            ' + LT + '/intent-filter>\n'
        + '        ' + LT + '/activity>\n'
        + '    ' + LT + '/application>\n'
        + LT + '/manifest' + GT + '\n'
    )
    write(ROOT / "app" / "src" / "main" / "AndroidManifest.xml", manifest_content)

    # 6. Resources & Source Code
    strings_content = (
        LT + '?xml version="1.0" encoding="utf-8"?' + GT + '\n'
        + LT + 'resources' + GT + '\n'
        + '    ' + LT + 'string name="app_name"' + GT + clean_app_name + LT + '/string' + GT + '\n'
        + LT + '/resources' + GT + '\n'
    )
    write(ROOT / "app" / "src" / "main" / "res" / "values" / "strings.xml", strings_content)
    write(ROOT / "app" / "src" / "main" / "res" / "values" / "colors.xml", COLORS_XML)
    write(ROOT / "app" / "src" / "main" / "res" / "drawable" / "ic_launcher.xml", IC_LAUNCHER_XML)
    write(ROOT / "app" / "src" / "main" / "res" / "layout" / "activity_main.xml", layout_xml)

    java_path = ROOT / "app" / "src" / "main" / "java" / pathlib.Path(*pkg.split("."))
    write(java_path / "MainActivity.java", main_java)

    print(f"[OK] Proyek Android {clean_app_name} ({pkg}) berhasil dibangun!")


if __name__ == "__main__":
    main()
