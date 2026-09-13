#!/usr/bin/env python3
"""
Generate Android native project (Java + XML) dari payload.json.
Bulletproof: Root direktori utama, package sinkron, auto-fix XML,
auto-escape Java literal, strings & colors resource valid murni.
"""
import json
import os
import pathlib
import re
import sys
import xml.etree.ElementTree as ET

ROOT = pathlib.Path(".")
PAYLOAD = pathlib.Path("payload.json")
PKG_NAME = "com.stb.dynamicapp"


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


# ---------- XML Helpers ----------
FALLBACK_LAYOUT = """


    

    


"""


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
    if not xml.startswith("]+>", "", raw_name)
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

    # 1. Gradle Project Settings
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

    # 2. App Module Build Configuration
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
    manifest_content = (
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
    write(ROOT / "app" / "src" / "main" / "AndroidManifest.xml", manifest_content)

    # 4. Resources (strings.xml HANYA berisi tag , colors.xml HANYA tag )
    strings_content = (
        '\n'
        '\n'
        f'    {clean_app_name}\n'
        '\n'
    )
    write(ROOT / "app" / "src" / "main" / "res" / "values" / "strings.xml", strings_content)

    colors_content = (
        '\n'
        '\n'
        '    #FF000000\n'
        '    #FFFFFFFF\n'
        '\n'
    )
    write(ROOT / "app" / "src" / "main" / "res" / "values" / "colors.xml", colors_content)

    icon_content = (
        '\n'
        '\n'
        '    \n'
        '    \n'
        '\n'
    )
    write(ROOT / "app" / "src" / "main" / "res" / "drawable" / "ic_launcher.xml", icon_content)
    write(ROOT / "app" / "src" / "main" / "res" / "layout" / "activity_main.xml", layout_xml)

    # 5. Java Source File
    java_path = ROOT / "app" / "src" / "main" / "java" / pathlib.Path(*pkg.split("."))
    write(java_path / "MainActivity.java", main_java)

    print(f"[OK] Proyek Android native berhasil dibuat di: {ROOT.resolve()}")
    print(f"[OK] Package: {pkg}")
    print(f"[OK] App Name: {clean_app_name}")


if __name__ == "__main__":
    main()
