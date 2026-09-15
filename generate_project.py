#!/usr/bin/env python3
"""
Generate Android native project (Java + XML) dari payload.json.
Lengkap:
- Auto-decode Base64 payload STB (xml_code_b64 & java_code_b64).
- Auto-generate ids.xml dari semua R.id.* Java (anti-cannot find symbol).
- Auto-harmonize nama ID XML (camelCase <-> snake_case).
- Auto-fix typo method listener CheckBox.
- Package name dinamis unik per aplikasi.
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


def die(msg, code=2):
    print(f"[FATAL] {msg}", file=sys.stderr)
    sys.exit(code)


def safe_get(d, keys, default=""):
    if not isinstance(d, dict):
        return default
    if isinstance(keys, str):
        keys = [keys]
    for k in keys:
        v = d.get(k)
        if v and isinstance(v, str) and v.strip():
            return v.strip()
    return default


def get_code_payload(d, b64_keys, plain_keys):
    if not isinstance(d, dict):
        return ""

    for k in b64_keys:
        val = d.get(k)
        if val and isinstance(val, str) and val.strip():
            try:
                dec = base64.b64decode(val.strip()).decode("utf-8", errors="ignore")
                if dec.strip():
                    return dec.strip()
            except Exception as e:
                print(f"[WARN] Gagal decode Base64 '{k}': {e}", file=sys.stderr)

    for k in plain_keys:
        val = d.get(k)
        if val and isinstance(val, str) and val.strip():
            s = val.strip()
            if len(s) > 50 and " " not in s and len(s) % 4 == 0:
                try:
                    dec = base64.b64decode(s).decode("utf-8", errors="ignore")
                    if "package " in dec or "class " in dec or "<" in dec:
                        return dec.strip()
                except Exception:
                    pass
            return s

    return ""


FALLBACK_LAYOUT = (
    '\n'
    '\n'
    '    \n'
    '    \n'
    '\n'
)

MANIFEST_TEMPLATE = (
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

COLORS_XML = (
    '\n'
    '\n'
    '    #FF000000\n'
    '    #FFFFFFFF\n'
    '\n'
)

IC_LAUNCHER_XML = (
    '\n'
    '\n'
    '    \n'
    '    \n'
    '\n'
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
    if not xml.startswith(" 60 else "")
            print(f"-> Key '{k}': {len(v)} karakter | {cuplikan}")
        else:
            print(f"-> Key '{k}': {repr(v)}")
    print("==================================================")

    # 1. Bersihkan Nama Aplikasi
    raw_name = safe_get(data, ["app_name", "title", "name"], "DynamicApp")
    clean_app_name = re.sub(r"[^\w\s-]", "", raw_name).strip()
    if not clean_app_name:
        clean_app_name = "DynamicApp"

    # 2. Package Name Dinamis
    pkg_suffix = re.sub(r"[^a-zA-Z0-9]", "", clean_app_name).lower()
    if len(pkg_suffix) < 3:
        pkg_suffix = "dynamicapp"
    pkg = f"com.stb.{pkg_suffix}"

    # 3. Baca Kode Layout & Java (Base64 / Plain)
    layout_raw = get_code_payload(
        data,
        b64_keys=["xml_code_b64", "layout_xml_b64", "activity_main_xml_b64", "layout_b64"],
        plain_keys=["activity_main_xml", "layout_xml", "layout", "xml", "code_xml"],
    )

    java_raw = get_code_payload(
        data,
        b64_keys=["java_code_b64", "main_activity_java_b64", "java_b64"],
        plain_keys=["main_activity_java", "java_code", "main_activity", "java", "code"],
    )

    print(f"[*] App Name        : {clean_app_name}")
    print(f"[*] Dynamic Package : {pkg}")
    print(f"[*] Decoded XML size: {len(layout_raw)} bytes")
    print(f"[*] Decoded Java size: {len(java_raw)} bytes")

    layout_xml = sanitize_layout(layout_raw)
    main_java = sanitize_java(java_raw, pkg)

    # 4. Sinkronisasi ID XML dengan panggilan di Java
    layout_xml = align_xml_ids_with_java(layout_xml, main_java)

    # 5. Settings & Build Gradle
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

    # 6. App Module Build Configuration
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

    # 7. AndroidManifest.xml
    write(ROOT / "app" / "src" / "main" / "AndroidManifest.xml", MANIFEST_TEMPLATE)

    # 8. Resources
    strings_content = (
        '\n'
        '\n'
        f'    {clean_app_name}\n'
        '\n'
    )
    write(ROOT / "app" / "src" / "main" / "res" / "values" / "strings.xml", strings_content)
    write(ROOT / "app" / "src" / "main" / "res" / "values" / "colors.xml", COLORS_XML)
    write(ROOT / "app" / "src" / "main" / "res" / "drawable" / "ic_launcher.xml", IC_LAUNCHER_XML)
    write(ROOT / "app" / "src" / "main" / "res" / "layout" / "activity_main.xml", layout_xml)

    # 9. Auto-generate ids.xml (Menjamin semua R.id.* yang dipanggil Java terdaftar di AAPT)
    java_ids = set(re.findall(r'R\.id\.([a-zA-Z0-9_]+)', main_java))
    if java_ids:
        items_xml = "\n".join([f'    ' for i in sorted(java_ids)])
        ids_content = (
            '\n'
            '\n'
            f'{items_xml}\n'
            '\n'
        )
        write(ROOT / "app" / "src" / "main" / "res" / "values" / "ids.xml", ids_content)
        print(f"[*] Berhasil mendaftarkan {len(java_ids)} ID ke res/values/ids.xml")

    # 10. Java Source File
    java_path = ROOT / "app" / "src" / "main" / "java" / pathlib.Path(*pkg.split("."))
    write(java_path / "MainActivity.java", main_java)

    print(f"[OK] Proyek Android {clean_app_name} ({pkg}) siap dikompilasi!")


if __name__ == "__main__":
    main()
