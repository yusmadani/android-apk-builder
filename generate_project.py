#!/usr/bin/env python3
"""
Generate Android native project (Java + XML) dari payload.json.
Bulletproof: Resource XML via Base64 murni, package sinkron, auto-fix XML,
auto-escape Java literal, bebas tag liar di strings.xml.
"""
import base64
import json
import os
import pathlib
import re
import sys
import xml.etree.ElementTree as ET

ROOT = pathlib.Path(".")
PAYLOAD = pathlib.Path("payload.json")
PKG_NAME = "com.stb.dynamicapp"
LT = chr(60)


def die(msg, code=2):
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


# 1. Fallback Layout (Base64)
FALLBACK_LAYOUT = base64.b64decode(
    "PD94bWwgdmVyc2lvbj0iMS4wIiBlbmNvZGluZz0idXRmLTgiPz4K"
    "PExpbmVhckxheW91dCB4bWxuczphbmRyb2lkPSJodHRwOi8vc2No"
    "ZW1hcy5hbmRyb2lkLmNvbS9hcGsvcmVzL2FuZHJvaWQiCiAgICBh"
    "bmRyb2lkOmxheW91dF93aWR0aD0ibWF0Y2hfcGFyZW50IgogICAg"
    "YW5kcm9pZDpsYXlvdXRfaGVpZ2h0PSJtYXRjaF9wYXJlbnQiCiAg"
    "ICBhbmRyb2lkOm9yaWVudGF0aW9uPSJ2ZXJ0aWNhbCIKICAgIGFu"
    "ZHJvaWQ6Z3Jhdml0eT0iY2VudGVyIgogICAgYW5kcm9pZDpwYWRk"
    "aW5nPSIyNGRwIj4KICAgIDxUZXh0VmlldwogICAgICAgIGFuZHJv"
    "aWQ6aWQ9IkAraWQvdHZUaXRsZSIKICAgICAgICBhbmRyb2lkOmxh"
    "eW91dF93aWR0aD0id3JhcF9jb250ZW50IgogICAgICAgIGFuZHJv"
    "aWQ6bGF5b3V0X2hlaWdodD0id3JhcF9jb250ZW50IgogICAgICAg"
    "IGFuZHJvaWQ6dGV4dD0iQHN0cmluZy9hcHBfbmFtZSIKICAgICAg"
    "ICBhbmRyb2lkOnRleHRTaXplPSIyMnNwIgogICAgICAgIGFuZHJv"
    "aWQ6dGV4dFN0eWxlPSJib2xkIiAvPgoKICAgIDxUZXh0Vmlldwog"
    "ICAgICAgIGFuZHJvaWQ6aWQ9IkAraWQvdHZNZXNzYWdlIgogICAg"
    "ICAgIGFuZHJvaWQ6bGF5b3V0X3dpZHRoPSJ3cmFwX2NvbnRlbnQi"
    "CiAgICAgICAgYW5kcm9pZDpsYXlvdXRfaGVpZ2h0PSJ3cmFwX2Nv"
    "bnRlbnQiCiAgICAgICAgYW5kcm9pZDpsYXlvdXRfbWFyZ2luVG9w"
    "PSIxMmRwIgogICAgICAgIGFuZHJvaWQ6dGV4dD0iQXBsaWthc2kg"
    "YmVyaGFzaWwgZGliYW5ndW4uIgogICAgICAgIGFuZHJvaWQ6dGV4"
    "dFNpemU9IjE2c3AiIC8+CjwvTGluZWFyTGF5b3V0Pgo="
).decode("utf-8")

# 2. Manifest (Base64)
MANIFEST_TEMPLATE = base64.b64decode(
    "PD94bWwgdmVyc2lvbj0iMS4wIiBlbmNvZGluZz0idXRmLTgiPz4K"
    "PG1hbmlmZXN0IHhtbG5zOmFuZHJvaWQ9Imh0dHA6Ly9zY2hlbWFz"
    "LmFuZHJvaWQuY29tL2Fway9yZXMvYW5kcm9pZCI+CiAgICA8YXBw"
    "bGljYXRpb24KICAgICAgICBhbmRyb2lkOmFsbG93QmFja3VwPSJ0"
    "cnVlIgogICAgICAgIGFuZHJvaWQ6aWNvbj0iQGRyYXdhYmxlL2lj"
    "X2xhdW5jaGVyIgogICAgICAgIGFuZHJvaWQ6bGFiZWw9IkBzdHJp"
    "bmcvYXBwX25hbWUiCiAgICAgICAgYW5kcm9pZDpzdXBwb3J0c1J0"
    "bD0idHJ1ZSIKICAgICAgICBhbmRyb2lkOnRoZW1lPSJAYW5kcm9p"
    "ZDpzdHlsZS9UaGVtZS5EZXZpY2VEZWZhdWx0Lk5vQWN0aW9uQmFy"
    "Ij4KICAgICAgICA8YWN0aXZpdHkKICAgICAgICAgICAgYW5kcm9p"
    "ZDpuYW1lPSIuTWFpbkFjdGl2aXR5IgogICAgICAgICAgICBhbmRy"
    "b2lkOmV4cG9ydGVkPSJ0cnVlIj4KICAgICAgICAgICAgPGludGVu"
    "dC1maWx0ZXI+CiAgICAgICAgICAgICAgICA8YWN0aW9uIGFuZHJv"
    "aWQ6bmFtZT0iYW5kcm9pZC5pbnRlbnQuYWN0aW9uLk1BSU4iIC8+"
    "CiAgICAgICAgICAgICAgICA8Y2F0ZWdvcnkgYW5kcm9pZDpuYW1l"
    "PSJhbmRyb2lkLmludGVudC5jYXRlZ29yeS5MQVVOQ0hFUiIgLz4K"
    "ICAgICAgICAgICAgPC9pbnRlbnQtZmlsdGVyPgogICAgICAgIDwv"
    "YWN0aXZpdHk+CiAgICA8L2FwcGxpY2F0aW9uPgo8L21hbmlmZXN0"
    "Pgo="
).decode("utf-8")

# 3. Colors XML (Base64 murni - tanpa karakter non-breaking space)
COLORS_XML = base64.b64decode(
    "PD94bWwgdmVyc2lvbj0iMS4wIiBlbmNvZGluZz0idXRmLTgiPz4K"
    "PHJlc291cmNlcz4KICAgIDxjb2xvciBuYW1lPSJibGFjayI+I0ZG"
    "MDAwMDAwPC9jb2xvcj4KICAgIDxjb2xvciBuYW1lPSJ3aGl0ZSI+"
    "I0ZGRkZGRkZGRjwvY29sb3I+CjwvcmVzb3VyY2VzPgo="
).decode("utf-8")

# 4. Strings XML Template (Base64)
STRINGS_XML_TEMPLATE = base64.b64decode(
    "PD94bWwgdmVyc2lvbj0iMS4wIiBlbmNvZGluZz0idXRmLTgiPz4K"
    "PHJlc291cmNlcz4KICAgIDxzdHJpbmcgbmFtZT0iYXBwX25hbWUi"
    "Pl9fQVBQX05BTUVfXzwvc3RyaW5nPgo8L3Jlc291cmNlcz4K"
).decode("utf-8")

# 5. Launcher Icon (Base64)
IC_LAUNCHER_XML = base64.b64decode(
    "PD94bWwgdmVyc2lvbj0iMS4wIiBlbmNvZGluZz0idXRmLTgiPz4K"
    "PHZlY3RvciB4bWxuczphbmRyb2lkPSJodHRwOi8vc2NoZW1hcy5h"
    "bmRyb2lkLmNvbS9hcGsvcmVzL2FuZHJvaWQiCiAgICBhbmRyb2lk"
    "OndpZHRoPSIxMDhkcCIKICAgIGFuZHJvaWQ6aGVpZ2h0PSIxMDhk"
    "cCIKICAgIGFuZHJvaWQ6dmlld3BvcnRXaWR0aD0iMTA4IgogICAg"
    "YW5kcm9pZDp2aWV3cG9ydEhlaWdodD0iMTA4Ij4KICAgIDxwYXRo"
    "CiAgICAgICAgYW5kcm9pZDpmaWxsQ29sb3I9IiMwMDg1NzciCiAg"
    "ICAgICAgYW5kcm9pZDpwYXRoRGF0YT0iTTAsMGgxMDh2MTA4aC0x"
    "MDh6Ii8+CiAgICA8cGF0aAogICAgICAgIGFuZHJvaWQ6ZmlsbENv"
    "bG9yPSIjRkZGRkZGIgogICAgICAgIGFuZHJvaWQ6cGF0aERhdGE9"
    "Ik01NCwyMEw3NCw0MEg2MFY3NEg0OFY0MEgzNEw1NCwyMFoiLz4K"
    "PC92ZWN0b3I+Cg=="
).decode("utf-8")


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
    header = LT + '?xml version="1.0" encoding="utf-8"?>\n'
    if not xml.startswith(LT + "?xml"):
        xml = header + xml
    return xml


def validate_xml(xml):
    try:
        ET.fromstring(xml)
        return True
    except Exception as e:
        print(f"[WARN] XML invalid: {e}", file=sys.stderr)
        return False


def sanitize_layout(raw_xml):
    xml = strip_code_fences(raw_xml)
    xml = ensure_root_xml(xml)
    if not xml or len(xml.strip()) < 30:
        print("[WARN] Layout kosong/terlalu pendek, memakai fallback.", file=sys.stderr)
        return FALLBACK_LAYOUT
    xml = fix_xml_escapes(xml)
    xml = fix_missing_id_prefix(xml)
    if not validate_xml(xml):
        print("[WARN] Layout rusak, memakai fallback.", file=sys.stderr)
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


def sanitize_java(raw_java, pkg):
    java = strip_code_fences(raw_java)
    if not java or "class " not in java:
        print("[WARN] Java kosong/tidak valid, memakai MainActivity fallback.", file=sys.stderr)
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

    # Bersihkan nama aplikasi: buang semua tag HTML/XML
    raw_name = safe_get(data, "app_name", "DynamicApp")
    clean_app_name = re.sub(r"<[^>]+>", "", raw_name)
    clean_app_name = (
        clean_app_name.replace("&", "&")
        .replace("'", "\\'")
        .replace('"', '\\"')
        .strip()
    )
    if not clean_app_name:
        clean_app_name = "DynamicApp"

    layout_raw = safe_get(data, "activity_main_xml", "")
    java_raw = safe_get(data, "main_activity_java", "")

    pkg = PKG_NAME
    layout_xml = sanitize_layout(layout_raw)
    main_java = sanitize_java(java_raw, pkg)

    # 1. Gradle Project Configuration
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

    # 2. App Module Configuration
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

    # 3. AndroidManifest.xml
    write(ROOT / "app" / "src" / "main" / "AndroidManifest.xml", MANIFEST_TEMPLATE)

    # 4. Resources
    strings_content = STRINGS_XML_TEMPLATE.replace("__APP_NAME__", clean_app_name)
    write(ROOT / "app" / "src" / "main" / "res" / "values" / "strings.xml", strings_content)
    write(ROOT / "app" / "src" / "main" / "res" / "values" / "colors.xml", COLORS_XML)
    write(ROOT / "app" / "src" / "main" / "res" / "drawable" / "ic_launcher.xml", IC_LAUNCHER_XML)
    write(ROOT / "app" / "src" / "main" / "res" / "layout" / "activity_main.xml", layout_xml)

    # 5. Java Source File
    java_path = ROOT / "app" / "src" / "main" / "java" / pathlib.Path(*pkg.split("."))
    write(java_path / "MainActivity.java", main_java)

    print(f"[OK] Proyek Android native berhasil dibuat di: {ROOT.resolve()}")
    print(f"[OK] Package: {pkg}")
    print(f"[OK] Layout XML bytes: {len(layout_xml)}")
    print(f"[OK] Java bytes: {len(main_java)}")


if __name__ == "__main__":
    main()
