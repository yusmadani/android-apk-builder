#!/usr/bin/env python3
"""
Universal Native Android Engine (Material 3 Kotlin Edition)
- Bahasa: Kotlin Murni + Google Material Design 3
- Tampilan: Standar Studio Pro (Dashboard, Master Data, Analytics)
- Adaptif: Konten otomatis menyesuaikan permintaan (Mengajar, Gym, Kasir, dll.)
- Ukuran: ~4.5 MB Native APK
"""
import os
import pathlib
import sys
import json
import re

ROOT = pathlib.Path(".")
PAYLOAD = pathlib.Path("payload.json")

LT = chr(60)
GT = chr(62)

def write(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")

def detect_app_domain(title):
    t = title.lower()
    if any(k in t for k in ["ajar", "sekolah", "guru", "jadwal", "kelas"]):
        return {
            "type": "teacher",
            "stat1_lbl": "TOTAL JADWAL", "stat1_val": "14",
            "stat2_lbl": "KELAS AKTIF", "stat2_val": "6",
            "stat3_lbl": "TOTAL RUANG", "stat3_val": "4",
            "item_title": "Daftar Jam Mengajar Hari Ini",
            "items": [
                ("07:15 - 08:45", "Pemrograman Web & Perangkat Bergerak", "XII RPL 1 • Lab Komputer 2"),
                ("09:00 - 10:30", "Basis Data Relasional", "XI RPL 2 • Lab Rekayasa"),
                ("10:45 - 12:15", "Pemodelan Perangkat Lunak", "X RPL 1 • Ruang Teori 04"),
                ("13:00 - 14:30", "Administrasi Server Jaringan", "XII TKJ 2 • Bengkel TKJ")
            ],
            "analysis_txt": "Rata-rata mengajar 5.5 Jam/Hari dengan utilitas ruangan 85%."
        }
    elif any(k in t for k in ["gym", "fit", "latihan", "otot", "workout"]):
        return {
            "type": "gym",
            "stat1_lbl": "TOTAL GERAKAN", "stat1_val": "8",
            "stat2_lbl": "SET SELESAI", "stat2_val": "3",
            "stat3_lbl": "ESTIMASI KKAL", "stat3_val": "420",
            "item_title": "Program Latihan Hari Ini",
            "items": [
                ("4 Set x 12 Reps", "Dumbbell Flat Bench Press", "Target: Dada • Beban: 22 Kg"),
                ("4 Set x 10 Reps", "Lat Pulldown Pulley", "Target: Punggung • Beban: 55 Kg"),
                ("3 Set x 15 Reps", "Triceps Cable Pushdown", "Target: Triceps • Beban: 35 Kg"),
                ("4 Set x 12 Reps", "Incline Dumbbell Curl", "Target: Biceps • Beban: 14 Kg")
            ],
            "analysis_txt": "Volume beban kumulatif hari ini meningkat 12% dibanding sesi kemarin."
        }
    else:
        return {
            "type": "general",
            "stat1_lbl": "TOTAL ENTRI", "stat1_val": "24",
            "stat2_lbl": "AKTIF / PROSES", "stat2_val": "18",
            "stat3_lbl": "SELESAI", "stat3_val": "6",
            "item_title": "Aktivitas Utama Terjadwal",
            "items": [
                ("08:00 - 09:30", "Review Item Operasional", "Prioritas: Tinggi • Tim Lapangan"),
                ("10:00 - 11:30", "Sinkronisasi Master Record", "Kategori: Inventaris Utama"),
                ("13:00 - 14:00", "Laporan Perkembangan Harian", "Status: Terjadwal Hari Ini")
            ],
            "analysis_txt": "Efisiensi alur sistem terpantau stabil pada 92% efektivitas operasional."
        }

def main():
    raw_name = "Jadwal Mengajar"
    if len(sys.argv) >= 2 and sys.argv[1]:
        raw_name = sys.argv[1]
    elif PAYLOAD.exists():
        try:
            data = json.loads(PAYLOAD.read_text(encoding="utf-8"))
            raw_name = data.get("app_name", "Jadwal Mengajar")
        except Exception:
            pass

    clean_name = re.sub(r"[^\w\s-]", "", raw_name).strip() or "Jadwal Mengajar"
    pkg_suffix = re.sub(r"[^a-zA-Z0-9]", "", clean_name).lower() or "centoaapp"
    pkg = f"com.centoa.{pkg_suffix}"

    domain = detect_app_domain(clean_name)

    # 1. Gradle Setup (Gradle 8.7 + AGP 8.5.2)
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
        f"rootProject.name = '{clean_name}'\n"
        "include ':app'\n"
    )

    write(ROOT / "build.gradle",
        "plugins {\n"
        "    id 'com.android.application' version '8.5.2' apply false\n"
        "    id 'org.jetbrains.kotlin.android' version '1.9.22' apply false\n"
        "}\n"
    )

    write(ROOT / "gradle.properties",
        "org.gradle.jvmargs=-Xmx2048m -Dfile.encoding=UTF-8\n"
        "android.useAndroidX=true\n"
        "android.nonTransitiveRClass=true\n"
        "kotlin.code.style=official\n"
    )

    # 2. App Gradle (Material 3 + Kotlin)
    write(ROOT / "app" / "build.gradle",
        "plugins {\n"
        "    id 'com.android.application'\n"
        "    id 'org.jetbrains.kotlin.android'\n"
        "}\n\n"
        "android {\n"
        f"    namespace '{pkg}'\n"
        "    compileSdk 34\n\n"
        "    defaultConfig {\n"
        f"        applicationId '{pkg}'\n"
        "        minSdk 24\n"
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
        "    kotlinOptions {\n"
        "        jvmTarget = '17'\n"
        "    }\n"
        "}\n\n"
        "dependencies {\n"
        "    implementation 'androidx.core:core-ktx:1.12.0'\n"
        "    implementation 'androidx.appcompat:appcompat:1.6.1'\n"
        "    implementation 'com.google.android.material:material:1.11.0'\n"
        "    implementation 'androidx.cardview:cardview:1.0.0'\n"
        "}\n"
    )

    # 3. Android Manifest
    write(ROOT / "app" / "src" / "main" / "AndroidManifest.xml",
        f"{LT}?xml version=\"1.0\" encoding=\"utf-8\"?{GT}\n"
        f"{LT}manifest xmlns:android=\"http://schemas.android.com/apk/res/android\"{GT}\n"
        f'    {LT}uses-permission android:name="android.permission.VIBRATE" /{GT}\n'
        f"    {LT}application\n"
        f'        android:allowBackup="true"\n'
        f'        android:icon="@drawable/ic_launcher"\n'
        f'        android:label="@string/app_name"\n'
        f'        android:theme="@style/Theme.ProStudio"{GT}\n'
        f"        {LT}activity\n"
        f'            android:name=".MainActivity"\n'
        f'            android:exported="true"{GT}\n'
        f"            {LT}intent-filter{GT}\n"
        f'                {LT}action android:name="android.intent.action.MAIN" /{GT}\n'
        f'                {LT}category android:name="android.intent.category.LAUNCHER" /{GT}\n'
        f"            {LT}/intent-filter{GT}\n"
        f"        {LT}/activity{GT}\n"
        f"    {LT}/application{GT}\n"
        f"{LT}/manifest{GT}\n"
    )

    # 4. Resources
    write(ROOT / "app" / "src" / "main" / "res" / "values" / "colors.xml",
        f"{LT}?xml version=\"1.0\" encoding=\"utf-8\"?{GT}\n"
        f"{LT}resources{GT}\n"
        f"    {LT}color name=\"studio_bg\"{GT}#0B111E{LT}/color{GT}\n"
        f"    {LT}color name=\"studio_card\"{GT}#141D2F{LT}/color{GT}\n"
        f"    {LT}color name=\"studio_primary\"{GT}#00E5FF{LT}/color{GT}\n"
        f"    {LT}color name=\"studio_secondary\"{GT}#7C4DFF{LT}/color{GT}\n"
        f"    {LT}color name=\"studio_emerald\"{GT}#00E676{LT}/color{GT}\n"
        f"    {LT}color name=\"studio_text\"{GT}#FFFFFF{LT}/color{GT}\n"
        f"    {LT}color name=\"studio_text_muted\"{GT}#8B9AB5{LT}/color{GT}\n"
        f"{LT}/resources{GT}\n"
    )

    write(ROOT / "app" / "src" / "main" / "res" / "values" / "styles.xml",
        f"{LT}?xml version=\"1.0\" encoding=\"utf-8\"?{GT}\n"
        f"{LT}resources{GT}\n"
        f'    {LT}style name="Theme.ProStudio" parent="Theme.Material3.DayNight.NoActionBar"{GT}\n'
        f'        {LT}item name="android:windowBackground"{GT}@color/studio_bg{LT}/item{GT}\n'
        f'        {LT}item name="android:statusBarColor"{GT}@color/studio_bg{LT}/item{GT}\n'
        f'        {LT}item name="android:navigationBarColor"{GT}@color/studio_card{LT}/item{GT}\n'
        f'        {LT}item name="colorPrimary"{GT}@color/studio_primary{LT}/item{GT}\n'
        f'        {LT}item name="colorSecondary"{GT}@color/studio_secondary{LT}/item{GT}\n'
        f"    {LT}/style{GT}\n"
        f"{LT}/resources{GT}\n"
    )

    write(ROOT / "app" / "src" / "main" / "res" / "values" / "strings.xml",
        f'{LT}resources{GT}{LT}string name="app_name"{GT}{clean_name}{LT}/string{GT}{LT}/resources{GT}'
    )

    write(ROOT / "app" / "src" / "main" / "res" / "drawable" / "ic_launcher.xml",
        f"{LT}?xml version=\"1.0\" encoding=\"utf-8\"?{GT}\n"
        f'{LT}vector xmlns:android="http://schemas.android.com/apk/res/android" android:width="108dp" android:height="108dp" android:viewportWidth="108" android:viewportHeight="108"{GT}\n'
        f'    {LT}path android:fillColor="#0B111E" android:pathData="M0,0h108v108h-108z"/{GT}\n'
        f'    {LT}path android:fillColor="#00E5FF" android:pathData="M30,30h48v48h-48z"/{GT}\n'
        f'    {LT}path android:fillColor="#7C4DFF" android:pathData="M44,44h20v20h-20z"/{GT}\n'
        f"{LT}/vector{GT}\n"
    )

    # 5. Native Layout (activity_main.xml)
    write(ROOT / "app" / "src" / "main" / "res" / "layout" / "activity_main.xml",
        f"{LT}?xml version=\"1.0\" encoding=\"utf-8\"?{GT}\n"
        f'{LT}RelativeLayout xmlns:android="http://schemas.android.com/apk/res/android"\n'
        f'    xmlns:app="http://schemas.android.com/apk/res-auto"\n'
        f'    android:layout_width="match_parent"\n'
        f'    android:layout_height="match_parent"\n'
        f'    android:background="@color/studio_bg"{GT}\n'
        f'    {LT}!-- TOP APP BAR --{GT}\n'
        f'    {LT}LinearLayout android:id="@+id/header_bar" android:layout_width="match_parent" android:layout_height="64dp" android:paddingHorizontal="20dp" android:gravity="center_vertical" android:background="@color/studio_bg"{GT}\n'
        f'        {LT}TextView android:layout_width="0dp" android:layout_height="wrap_content" android:layout_weight="1" android:text="{clean_name}" android:textColor="@color/studio_primary" android:textSize="20sp" android:textStyle="bold" /{GT}\n'
        f'        {LT}TextView android:id="@+id/clock_text" android:layout_width="wrap_content" android:layout_height="wrap_content" android:text="00:00:00" android:textColor="@color/studio_emerald" android:textSize="14sp" android:textStyle="bold" /{GT}\n'
        f'    {LT}/LinearLayout{GT}\n'
        f'    {LT}!-- SCROLLABLE CONTENT --{GT}\n'
        f'    {LT}ScrollView android:layout_width="match_parent" android:layout_height="match_parent" android:layout_below="@id/header_bar" android:layout_above="@id/nav_bar"{GT}\n'
        f'        {LT}LinearLayout android:layout_width="match_parent" android:layout_height="wrap_content" android:orientation="vertical" android:padding="16dp"{GT}\n'
        f'            {LT}!-- VIEW TAB 1: DASHBOARD --{GT}\n'
        f'            {LT}LinearLayout android:id="@+id/view_tab_dashboard" android:layout_width="match_parent" android:layout_height="wrap_content" android:orientation="vertical"{GT}\n'
        f'                {LT}LinearLayout android:layout_width="match_parent" android:layout_height="wrap_content" android:orientation="horizontal" android:weightSum="3" android:layout_marginBottom="16dp"{GT}\n'
        f'                    {LT}androidx.cardview.widget.CardView android:layout_width="0dp" android:layout_height="85dp" android:layout_weight="1" app:cardCornerRadius="14dp" app:cardBackgroundColor="@color/studio_card" app:cardElevation="0dp"{GT}\n'
        f'                        {LT}LinearLayout android:layout_width="match_parent" android:layout_height="match_parent" android:gravity="center" android:orientation="vertical"{GT}\n'
        f'                            {LT}TextView android:layout_width="wrap_content" android:layout_height="wrap_content" android:text="{domain["stat1_val"]}" android:textColor="@color/studio_primary" android:textSize="22sp" android:textStyle="bold" /{GT}\n'
        f'                            {LT}TextView android:layout_width="wrap_content" android:layout_height="wrap_content" android:text="{domain["stat1_lbl"]}" android:textColor="@color/studio_text_muted" android:textSize="10sp" android:textStyle="bold" /{GT}\n'
        f'                        {LT}/LinearLayout{GT}\n'
        f'                    {LT}/androidx.cardview.widget.CardView{GT}\n'
        f'                    {LT}androidx.cardview.widget.CardView android:layout_width="0dp" android:layout_height="85dp" android:layout_weight="1" android:layout_marginStart="8dp" app:cardCornerRadius="14dp" app:cardBackgroundColor="@color/studio_card" app:cardElevation="0dp"{GT}\n'
        f'                        {LT}LinearLayout android:layout_width="match_parent" android:layout_height="match_parent" android:gravity="center" android:orientation="vertical"{GT}\n'
        f'                            {LT}TextView android:layout_width="wrap_content" android:layout_height="wrap_content" android:text="{domain["stat2_val"]}" android:textColor="@color/studio_emerald" android:textSize="22sp" android:textStyle="bold" /{GT}\n'
        f'                            {LT}TextView android:layout_width="wrap_content" android:layout_height="wrap_content" android:text="{domain["stat2_lbl"]}" android:textColor="@color/studio_text_muted" android:textSize="10sp" android:textStyle="bold" /{GT}\n'
        f'                        {LT}/LinearLayout{GT}\n'
        f'                    {LT}/androidx.cardview.widget.CardView{GT}\n'
        f'                    {LT}androidx.cardview.widget.CardView android:layout_width="0dp" android:layout_height="85dp" android:layout_weight="1" android:layout_marginStart="8dp" app:cardCornerRadius="14dp" app:cardBackgroundColor="@color/studio_card" app:cardElevation="0dp"{GT}\n'
        f'                        {LT}LinearLayout android:layout_width="match_parent" android:layout_height="match_parent" android:gravity="center" android:orientation="vertical"{GT}\n'
        f'                            {LT}TextView android:layout_width="wrap_content" android:layout_height="wrap_content" android:text="{domain["stat3_val"]}" android:textColor="@color/studio_secondary" android:textSize="22sp" android:textStyle="bold" /{GT}\n'
        f'                            {LT}TextView android:layout_width="wrap_content" android:layout_height="wrap_content" android:text="{domain["stat3_lbl"]}" android:textColor="@color/studio_text_muted" android:textSize="10sp" android:textStyle="bold" /{GT}\n'
        f'                        {LT}/LinearLayout{GT}\n'
        f'                    {LT}/androidx.cardview.widget.CardView{GT}\n'
        f'                {LT}/LinearLayout{GT}\n'
        f'            {LT}/LinearLayout{GT}\n'
        f'            {LT}!-- VIEW TAB 2: DAFTAR DATA UTAMA --{GT}\n'
        f'            {LT}LinearLayout android:id="@+id/view_tab_data" android:layout_width="match_parent" android:layout_height="wrap_content" android:orientation="vertical"{GT}\n'
        f'                {LT}TextView android:layout_width="wrap_content" android:layout_height="wrap_content" android:text="{domain["item_title"]}" android:textColor="@color/studio_text" android:textSize="16sp" android:textStyle="bold" android:layout_marginBottom="12dp" /{GT}\n'
        f'                {LT}LinearLayout android:id="@+id/item_container" android:layout_width="match_parent" android:layout_height="wrap_content" android:orientation="vertical" /{GT}\n'
        f'            {LT}/LinearLayout{GT}\n'
        f'            {LT}!-- VIEW TAB 3: ANALISIS & AKSI --{GT}\n'
        f'            {LT}LinearLayout android:id="@+id/view_tab_analysis" android:layout_width="match_parent" android:layout_height="wrap_content" android:orientation="vertical" android:visibility="gone"{GT}\n'
        f'                {LT}androidx.cardview.widget.CardView android:layout_width="match_parent" android:layout_height="wrap_content" app:cardCornerRadius="16dp" app:cardBackgroundColor="@color/studio_card" app:cardElevation="0dp"{GT}\n'
        f'                    {LT}LinearLayout android:layout_width="match_parent" android:layout_height="wrap_content" android:padding="18dp" android:orientation="vertical"{GT}\n'
        f'                        {LT}TextView android:layout_width="wrap_content" android:layout_height="wrap_content" android:text="Ringkasan Kinerja & Evaluasi" android:textColor="@color/studio_primary" android:textSize="16sp" android:textStyle="bold" /{GT}\n'
        f'                        {LT}TextView android:layout_width="wrap_content" android:layout_height="wrap_content" android:text="{domain["analysis_txt"]}" android:textColor="@color/studio_text_muted" android:textSize="13sp" android:layout_marginTop="8dp" android:lineSpacingExtra="4dp" /{GT}\n'
        f'                        {LT}Button android:id="@+id/btn_action_demo" android:layout_width="match_parent" android:layout_height="50dp" android:text="Sinkronisasi Data Otomatis" android:textColor="#0B111E" android:textStyle="bold" android:backgroundTint="@color/studio_primary" android:layout_marginTop="16dp" /{GT}\n'
        f'                    {LT}/LinearLayout{GT}\n'
        f'                {LT}/androidx.cardview.widget.CardView{GT}\n'
        f'            {LT}/LinearLayout{GT}\n'
        f'        {LT}/LinearLayout{GT}\n'
        f'    {LT}/ScrollView{GT}\n'
        f'    {LT}!-- BOTTOM NAVIGATION TAB BAR --{GT}\n'
        f'    {LT}LinearLayout android:id="@+id/nav_bar" android:layout_width="match_parent" android:layout_height="64dp" android:layout_alignParentBottom="true" android:background="@color/studio_card" android:orientation="horizontal" android:weightSum="3"{GT}\n'
        f'        {LT}TextView android:id="@+id/nav_dashboard" android:layout_width="0dp" android:layout_height="match_parent" android:layout_weight="1" android:gravity="center" android:text="DASHBOARD" android:textColor="@color/studio_primary" android:textSize="12sp" android:textStyle="bold" android:clickable="true" android:focusable="true" /{GT}\n'
        f'        {LT}TextView android:id="@+id/nav_data" android:layout_width="0dp" android:layout_height="match_parent" android:layout_weight="1" android:gravity="center" android:text="KELOLA" android:textColor="@color/studio_text_muted" android:textSize="12sp" android:textStyle="bold" android:clickable="true" android:focusable="true" /{GT}\n'
        f'        {LT}TextView android:id="@+id/nav_analysis" android:layout_width="0dp" android:layout_height="match_parent" android:layout_weight="1" android:gravity="center" android:text="ANALISIS" android:textColor="@color/studio_text_muted" android:textSize="12sp" android:textStyle="bold" android:clickable="true" android:focusable="true" /{GT}\n'
        f'    {LT}/LinearLayout{GT}\n'
        f"{LT}/RelativeLayout{GT}\n"
    )

    # 6. MainActivity Kotlin
    src_dir = ROOT / "app" / "src" / "main" / "java" / pathlib.Path(*pkg.split("."))
    
    # Format data list items untuk dimasukkan ke Kotlin
    items_kt = []
    for badge, title, desc in domain["items"]:
        items_kt.append(f'            addItem("{badge}", "{title}", "{desc}")')
    items_code = "\n".join(items_kt)

    kt_code = f"""package {pkg}

import android.app.Activity
import android.content.Context
import android.graphics.Color
import android.os.Bundle
import android.os.Handler
import android.os.Looper
import android.os.Vibrator
import android.view.View
import android.widget.Button
import android.widget.LinearLayout
import android.widget.TextView
import android.widget.Toast
import androidx.cardview.widget.CardView
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale

class MainActivity : Activity() {{
    private lateinit var clockText: TextView
    private lateinit var navDashboard: TextView
    private lateinit var navData: TextView
    private lateinit var navAnalysis: TextView
    private lateinit var viewDashboard: LinearLayout
    private lateinit var viewData: LinearLayout
    private lateinit var viewAnalysis: LinearLayout
    private lateinit var itemContainer: LinearLayout
    private lateinit var btnAction: Button
    private var vibrator: Vibrator? = null
    private val handler = Handler(Looper.getMainLooper())

    override fun onCreate(savedInstanceState: Bundle?) {{
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        vibrator = getSystemService(Context.VIBRATOR_SERVICE) as? Vibrator
        clockText = findViewById(R.id.clock_text)
        navDashboard = findViewById(R.id.nav_dashboard)
        navData = findViewById(R.id.nav_data)
        navAnalysis = findViewById(R.id.nav_analysis)
        viewDashboard = findViewById(R.id.view_tab_dashboard)
        viewData = findViewById(R.id.view_tab_data)
        viewAnalysis = findViewById(R.id.view_tab_analysis)
        itemContainer = findViewById(R.id.item_container)
        btnAction = findViewById(R.id.btn_action_demo)

        startClock()
        setupNavigation()
        populateItems()

        btnAction.setOnClickListener {{
            vibrate()
            Toast.makeText(this, "Data Berhasil Dimutakhirkan!", Toast.LENGTH_SHORT).show()
        }}
    }}

    private fun startClock() {{
        handler.post(object : Runnable {{
            override fun run() {{
                val time = SimpleDateFormat("HH:mm:ss", Locale.getDefault()).format(Date())
                clockText.text = time
                handler.postDelayed(this, 1000)
            }}
        }})
    }}

    private fun setupNavigation() {{
        navDashboard.setOnClickListener {{
            vibrate()
            viewDashboard.visibility = View.VISIBLE
            viewData.visibility = View.VISIBLE
            viewAnalysis.visibility = View.GONE
            updateNav(navDashboard)
        }}

        navData.setOnClickListener {{
            vibrate()
            viewDashboard.visibility = View.GONE
            viewData.visibility = View.VISIBLE
            viewAnalysis.visibility = View.GONE
            updateNav(navData)
        }}

        navAnalysis.setOnClickListener {{
            vibrate()
            viewDashboard.visibility = View.GONE
            viewData.visibility = View.GONE
            viewAnalysis.visibility = View.VISIBLE
            updateNav(navAnalysis)
        }}
    }}

    private fun updateNav(active: TextView) {{
        val dim = Color.parseColor("#8B9AB5")
        val cyan = Color.parseColor("#00E5FF")
        navDashboard.setTextColor(dim)
        navData.setTextColor(dim)
        navAnalysis.setTextColor(dim)
        active.setTextColor(cyan)
    }}

    private fun vibrate() {{
        vibrator?.vibrate(30)
    }}

    private fun populateItems() {{
        itemContainer.removeAllViews()
{items_code}
    }}

    private fun addItem(badge: String, title: String, subtitle: String) {{
        val card = CardView(this).apply {{
            radius = 28f
            setCardBackgroundColor(Color.parseColor("#141D2F"))
            cardElevation = 0f
        }}

        val layout = LinearLayout(this).apply {{
            orientation = LinearLayout.VERTICAL
            setPadding(36, 28, 36, 28)
        }}

        val badgeView = TextView(this).apply {{
            text = badge
            setTextColor(Color.parseColor("#00E676"))
            textSize = 11f
        }}

        val titleView = TextView(this).apply {{
            text = title
            setTextColor(Color.WHITE)
            textSize = 15f
            setPadding(0, 6, 0, 4)
        }}

        val subView = TextView(this).apply {{
            text = subtitle
            setTextColor(Color.parseColor("#8B9AB5"))
            textSize = 12f
        }}

        layout.addView(badgeView)
        layout.addView(titleView)
        layout.addView(subView)
        card.addView(layout)

        val params = LinearLayout.LayoutParams(
            LinearLayout.LayoutParams.MATCH_PARENT,
            LinearLayout.LayoutParams.WRAP_CONTENT
        ).apply {{
            setMargins(0, 0, 0, 20)
        }}

        card.layoutParams = params
        card.setOnClickListener {{
            vibrate()
            Toast.makeText(this, title, Toast.LENGTH_SHORT).show()
        }}

        itemContainer.addView(card)
    }}
}}
"""
    write(src_dir / "MainActivity.kt", kt_code)
    print(f"[OK] Material 3 Native Project siap untuk {clean_name} ({pkg})")

if __name__ == "__main__":
    main()
