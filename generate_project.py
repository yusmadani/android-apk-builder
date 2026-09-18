#!/usr/bin/env python3
"""
Generate Android native project (Java + XML) dari payload.json.
Fitur:
- Auto-clean karakter illegal Unicode (U+2216 / ∖, zero-width space, smart quotes).
- Auto-sync nama variabel WebView (∖view / view / webView).
- Auto-decode Base64 STB (xml_code_b64 & java_code_b64).
- Auto-fix typo WebView (private WebView.webView -> private WebView webView).
- Auto-fix titik liar ekspresi assignment (=. -> = ).
- Auto-inject import Android WebView & WebSettings.
- Manifest dengan izin INTERNET & Cleartext Traffic.
- Auto-fix listener CheckBox (setOnbuttonCheckedChangeListener).
- Auto-generate ids.xml (anti-cannot find symbol).
- 100% bebas karakter sudut mentah (kebal pemotongan clipboard/browser).
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

LT = chr(60)
GT = chr(62)


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
            if len(s) not in range(51) and " " not in s and len(s) % 4 == 0:
                try:
                    dec = base64.b64decode(s).decode("utf-8", errors="ignore")
                    if "package " in dec or "class " in dec or LT in dec:
                        return dec.strip()
                except Exception:
                    pass
            return s

    return ""


# Template Resource Terenkapsulasi (Bebas Karakter Sudut Mentah)
FALLBACK_LAYOUT = (
    f"{LT}?xml version=\"1.0\" encoding=\"utf-8\"?{GT}\n"
    f"{LT}LinearLayout xmlns:android=\"http://schemas.android.com/apk/res/android\"\n"
    f"    android:layout_width=\"match_parent\"\n"
    f"    android:layout_height=\"match_parent\"\n"
    f"    android:orientation=\"vertical\"\n"
    f"    android:gravity=\"center\"\n"
    f"    android:padding=\"24dp\"{GT}\n\n"
    f"    {LT}TextView\n"
    f"        android:id=\"@+id/tvTitle\"\n"
    f"        android:layout_width=\"wrap_content\"\n"
    f"        android:layout_height=\"wrap_content\"\n"
    f"        android:text=\"@string/app_name\"\n"
    f"        android:textSize=\"22sp\"\n"
    f"        android:textStyle=\"bold\" /{GT}\n\n"
    f"    {LT}TextView\n"
    f"        android:id=\"@+id/tvMessage\"\n"
    f"        android:layout_width=\"wrap_content\"\n"
    f"        android:layout_height=\"wrap_content\"\n"
    f"        android:layout_marginTop=\"12dp\"\n"
    f"        android:text=\"Aplikasi berhasil dibangun.\"\n"
    f"        android:textSize=\"16sp\" /{GT}\n\n"
    f"{LT}/LinearLayout{GT}\n"
)

MANIFEST_TEMPLATE = (
    f"{LT}?xml version=\"1.0\" encoding=\"utf-8\"?{GT}\n"
    f"{LT}manifest xmlns:android=\"http://schemas.android.com/apk/res/android\"{GT}\n"
    f"    {LT}uses-permission android:name=\"android.permission.INTERNET\" /{GT}\n"
    f"    {LT}application\n"
    f"        android:allowBackup=\"true\"\n"
    f"        android:icon=\"@drawable/ic_launcher\"\n"
    f"        android:label=\"@string/app_name\"\n"
    f"        android:supportsRtl=\"true\"\n"
    f"        android:usesCleartextTraffic=\"true\"\n"
    f"        android:theme=\"@android:style/Theme.DeviceDefault.NoActionBar\"{GT}\n"
    f"        {LT}activity\n"
    f"            android:name=\".MainActivity\"\n"
    f"            android:exported=\"true\"{GT}\n"
    f"            {LT}intent-filter{GT}\n"
    f"                {LT}action android:name=\"android.intent.action.MAIN\" /{GT}\n"
    f"                {LT}category android:name=\"android.intent.category.LAUNCHER\" /{GT}\n"
    f"            {LT}/intent-filter{GT}\n"
    f"        {LT}/activity{GT}\n"
    f"    {LT}/application{GT}\n"
    f"{LT}/manifest{GT}\n"
)

COLORS_XML = (
    f"{LT}?xml version=\"1.0\" encoding=\"utf-8\"?{GT}\n"
    f"{LT}resources{GT}\n"
    f"    {LT}color name=\"black\"{GT}#FF000000{LT}/color{GT}\n"
    f"    {LT}color name=\"white\"{GT}#FFFFFFFF{LT}/color{GT}\n"
    f"{LT}/resources{GT}\n"
)

IC_LAUNCHER_XML = (
    f"{LT}?xml version=\"1.0\" encoding=\"utf-8\"?{GT}\n"
    f"{LT}vector xmlns:android=\"http://schemas.android.com/apk/res/android\"\n"
    f"    android:width=\"108dp\"\n"
    f"    android:height=\"108dp\"\n"
    f"    android:viewportWidth=\"108\"\n"
    f"    android:viewportHeight=\"108\"{GT}\n"
    f"    {LT}path\n"
    f"        android:fillColor=\"#008577\"\n"
    f"        android:pathData=\"M0,0h108v108h-108z\"/{GT}\n"
    f"    {LT}path\n"
    f"        android:fillColor=\"#FFFFFF\"\n"
    f"        android:pathData=\"M54,20L74,40H60V74H48V40H34L54,20Z\"/{GT}\n"
    f"{LT}/vector{GT}\n"
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
    xml = xml.replace("&", "&amp;")
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
    decl_prefix = f"{LT}?xml"
    if not xml.startswith(decl_prefix):
        header = f"{LT}?xml version=\"1.0\" encoding=\"utf-8\"?{GT}\n"
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
    if len(xml.strip()) in range(30):
        print("[WARN] Layout kosong/terlalu pendek! Memakai fallback.", file=sys.stderr)
        return FALLBACK_LAYOUT
    xml = fix_xml_escapes(xml)
    xml = fix_missing_id_prefix(xml)
    if not validate_xml(xml):
        print("[WARN] Format XML rusak! Memakai fallback.", file=sys.stderr)
        return FALLBACK_LAYOUT
    return xml


def align_xml_ids_with_java(layout_xml, main_java):
    if not layout_xml or not main_java:
        return layout_xml

    java_ids = set(re.findall(r'R\.id\.([a-zA-Z0-9_]+)', main_java))
    if not java_ids:
        return layout_xml

    def repl(m):
        prefix = m.group(1)
        curr_id = m.group(2)
        snake = re.sub(r'([A-Z])', r'_\1', curr_id).lower().lstrip('_')
        if snake in java_ids:
            return f'{prefix}{snake}"'
        camel = re.sub(r'_([a-z])', lambda x: x.group(1).upper(), curr_id)
        if camel in java_ids:
            return f'{prefix}{camel}"'
        return m.group(0)

    return re.sub(r'(android:id="@\+id/)([^"]+)"', repl, layout_xml)


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
        print("[WARN] Java kosong/hilang! Memakai fallback MainActivity.", file=sys.stderr)
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

    # 1. Bersihkan karakter Unicode tersembunyi/illegal (U+2216, zero-width, smart quotes)
    java = java.replace('\u200b', '')   # Zero-width space
    java = java.replace('\ufeff', '')   # BOM
    java = java.replace('\u00a0', ' ')  # Non-breaking space
    java = java.replace('“', '"').replace('”', '"')
    java = java.replace('‘', "'").replace('’', "'")

    # 2. Koreksi variabel yang diawali karakter illegal \u2216 (∖) atau backslash
    java = re.sub(r'[\u2216\\]+([a-zA-Z_])', r'\1', java)
    java = java.replace('\u2216', '')

    # 3. Koreksi Typo Deklarasi Variabel dari AI (private WebView.webView; -> private WebView webView;)
    java = re.sub(r'\b(private|protected|public)\s+([A-Z]\w*)\.([a-z]\w*)\s*;', r'\1 \2 \3;', java)

    # 4. Koreksi Titik Liar Pada Ekspresi Penugasan (=.webView -> = webView)
    java = re.sub(r'=\s*\.\s*([a-zA-Z_])', r'= \1', java)

    # 5. Sinkronisasi nama variabel WebView antara deklarasi dan penggunaan
    if "private WebView webView;" in java or "WebView webView;" in java:
        java = re.sub(r'\bview\s*=\s*findViewById', 'webView = findViewById', java)
        java = re.sub(r'\bview\.(getSettings|loadUrl|setWebViewClient|setWebChromeClient)', r'webView.\1', java)
    elif "private WebView view;" in java or "WebView view;" in java:
        java = re.sub(r'\bwebView\s*=\s*findViewById', 'view = findViewById', java)
        java = re.sub(r'\bwebView\.(getSettings|loadUrl|setWebViewClient|setWebChromeClient)', r'view.\1', java)
    elif "WebView" in java:
        # Jika ada pemanggilan WebView tapi lupa dideklarasikan sebagai field
        if re.search(r'\b(webView|view)\s*=\s*findViewById', java):
            java = re.sub(r'(class\s+\w+\s+extends\s+\w+\s*\{)', r'\1\n    private WebView webView;', java)
            java = re.sub(r'\bview\s*=\s*findViewById', 'webView = findViewById', java)
            java = re.sub(r'\bview\.(getSettings|loadUrl|setWebViewClient|setWebChromeClient)', r'webView.\1', java)

    # 6. Koreksi Typo Method Listener CheckBox
    java = re.sub(r'setOnbuttonCheckedChangeListener', 'setOnCheckedChangeListener', java, flags=re.IGNORECASE)
    java = re.sub(r'setOnCheckChangeListener', 'setOnCheckedChangeListener', java, flags=re.IGNORECASE)

    # 7. Sinkronkan Nama Package
    if re.search(r"package\s+[\w\.]+;", java):
        java = re.sub(r"package\s+[\w\.]+;", f"package {pkg};", java)
    else:
        java = f"package {pkg};\n\n" + java

    # 8. Normalisasi Activity Turunan
    java = re.sub(r"extends\s+AppCompatActivity", "extends Activity", java)
    java = re.sub(r"import\s+androidx\.appcompat\.app\.AppCompatActivity;", "", java)

    # 9. Injeksi Import Android Esensial & WebView
    essential_imports = [
        "import android.app.Activity;",
        "import android.os.Bundle;",
        "import android.view.View;",
        "import android.widget.*;",
    ]
    if "WebView" in java:
        essential_imports.extend([
            "import android.webkit.WebView;",
            "import android.webkit.WebSettings;",
            "import android.webkit.WebViewClient;",
        ])

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

    print("==================================================")
    print("=== ISI PAYLOAD.JSON YANG DITERIMA DARI STB ===")
    print("Daftar Kunci (Keys):", list(data.keys()))
    for k, v in data.items():
        if isinstance(v, str):
            cuplikan = repr(v[:50]) + ("..." if len(v) not in range(51) else "")
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
    if len(pkg_suffix) in (0, 1, 2):
        pkg_suffix = "dynamicapp"
    pkg = f"com.stb.{pkg_suffix}"

    # 3. Baca Kode Layout & Java (Mendukung Base64 STB)
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

    # 4. Sinkronisasi ID XML dengan pemanggilan Java
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

    # 7. AndroidManifest.xml (Termasuk izin Internet & Cleartext Traffic)
    write(ROOT / "app" / "src" / "main" / "AndroidManifest.xml", MANIFEST_TEMPLATE)

    # 8. Resources
    strings_content = (
        f"{LT}?xml version=\"1.0\" encoding=\"utf-8\"?{GT}\n"
        f"{LT}resources{GT}\n"
        f"    {LT}string name=\"app_name\"{GT}{clean_app_name}{LT}/string{GT}\n"
        f"{LT}/resources{GT}\n"
    )
    write(ROOT / "app" / "src" / "main" / "res" / "values" / "strings.xml", strings_content)
    write(ROOT / "app" / "src" / "main" / "res" / "values" / "colors.xml", COLORS_XML)
    write(ROOT / "app" / "src" / "main" / "res" / "drawable" / "ic_launcher.xml", IC_LAUNCHER_XML)
    write(ROOT / "app" / "src" / "main" / "res" / "layout" / "activity_main.xml", layout_xml)

    # 9. Auto-generate ids.xml (Mencegah error AAPT/javac symbol missing)
    java_ids = set(re.findall(r'R\.id\.([a-zA-Z0-9_]+)', main_java))
    if java_ids:
        item_rows = [f'    {LT}item name="{i}" type="id"/{GT}' for i in sorted(java_ids)]
        items_block = "\n".join(item_rows)
        ids_content = (
            f"{LT}?xml version=\"1.0\" encoding=\"utf-8\"?{GT}\n"
            f"{LT}resources{GT}\n"
            f"{items_block}\n"
            f"{LT}/resources{GT}\n"
        )
        write(ROOT / "app" / "src" / "main" / "res" / "values" / "ids.xml", ids_content)
        print(f"[*] Berhasil mendaftarkan {len(java_ids)} ID ke res/values/ids.xml")

    # 10. Java Source File
    java_path = ROOT / "app" / "src" / "main" / "java" / pathlib.Path(*pkg.split("."))
    write(java_path / "MainActivity.java", main_java)

    print(f"[OK] Proyek Android {clean_app_name} ({pkg}) siap dikompilasi!")


if __name__ == "__main__":
    main()
