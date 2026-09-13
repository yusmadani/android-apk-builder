#!/usr/bin/env python3
"""
Generate Android native project (Java + XML) dari payload.json.
Bulletproof: paket seragam, bebas spasi non-standar, auto-fix XML,
auto-escape Java literal, manifest bersih, dan fallback aman.
"""
import json
import os
import re
import pathlib
import sys
import xml.etree.ElementTree as ET

ROOT = pathlib.Path("project")
PAYLOAD = pathlib.Path("payload.json")
PKG_NAME = "com.stb.dynamicapp"  # Kunci paket agar sinkron dengan bot dan Manifest


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


# ---------- XML Helpers ----------
FALLBACK_LAYOUT = """


    

    


"""


def strip_code_fences(s: str) -> str:
    if not isinstance(s, str):
        return ""
    s = s.strip()
    s = re.sub(r"^```[a-zA-Z0-9_+-]*\s*", "", s)
    s = re.sub(r"\s*```$", "", s)
    return s.strip()


def fix_xml_escapes(xml: str) -> str:
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


def fix_missing_id_prefix(xml: str) -> str:
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
    if not xml.startswith(" bool:
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


# ---------- Java Helpers ----------
def sanitize_java_strings(java: str) -> str:
    if not java:
        return java
    java = strip_code_fences(java)
    java = java.replace("\r\n", "\n").replace("\r", "\n")

    # Rekatkan baris string yang terpotong enter fisik
    java = re.sub(r'"\s*\n\s*', '" + "', java)

    # Escape newline di dalam kutip
    out = []
    in_str = False
    i = 0
    n = len(java)
    while i < n:
        c = java[i]
        if in_str:
            if c == '\\' and i + 1 < n:
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


def sanitize_java(raw_java: str, pkg: str) -> str:
    java = strip_code_fences(raw_java)
    if not java or "class " not in java:
        print("[WARN] Java kosong/tidak valid, pakai MainActivity fallback.", file=sys.stderr)
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

    # Paksa package name seragam
    if re.search(r"package\s+[\w\.]+;", java):
        java = re.sub(r"package\s+[\w\.]+;", f"package {pkg};", java)
    else:
        java = f"package {pkg};\n\n" + java

    # Pastikan extends Activity biasa (anti-crash dengan tema native)
    java = re.sub(r"extends\s+AppCompatActivity", "extends Activity", java)
    java = re.sub(r"import\s+androidx\.appcompat\.app\.AppCompatActivity;", "", java)

    # Tambahkan import umum jika terlewat oleh AI
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
    safe_app_name = app_name.replace("&", "&").replace("'", "\\'")

    layout_raw = safe_get(data, "activity_main_xml", "")
    java_raw = safe_get(data, "main_activity_java", "")

    pkg = PKG_NAME
    layout_xml = sanitize_layout(layout_raw)
    main_java = sanitize_java(java_raw, pkg)

    # 1. Root Project
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
        "rootProject.name = 'DynamicApp'\n"
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

    # 2. App Module
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

    # 3. AndroidManifest.xml (Bersih tanpa spasi awal)
    manifest = (
        '\n'
        '\n'
        '    \n'
        '        \n'
        '            \n'
        '                \n'
        '                \n'
        '            \n'
        '        \n'
        '    \n'
        '\n'
    )
    write(ROOT / "app" / "src" / "main" / "AndroidManifest.xml", manifest)

    # 4. Resources
    write(ROOT / "app" / "src" / "main" / "res" / "values" / "strings.xml", (
        '\n'
        '\n'
        f'    {safe_app_name}\n'
        '\n'
    ))

    write(ROOT / "app" / "src" / "main" / "res" / "values" / "colors.xml", (
        '\n'
        '\n'
        '    #FF000000\n'
        '    #FFFFFFFF\n'
        '\n'
    ))

    write(ROOT / "app" / "src" / "main" / "res" / "layout" / "activity_main.xml", layout_xml)

    # 5. Java Source File
    java_path = ROOT / "app" / "src" / "main" / "java" / pathlib.Path(*pkg.split("."))
    write(java_path / "MainActivity.java", main_java)

    print("[OK] Project berhasil digenerate di:", ROOT.resolve())
    print("[OK] Package:", pkg)


if __name__ == "__main__":
    main()
