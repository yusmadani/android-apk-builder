#!/usr/bin/env python3
"""
Native Android Generator (Cyberpunk Edition - Active Navigation & PDF Export)
- Menu Tab Interaktif (Dashboard, Jadwal, Export PDF).
- Room SQLite Database.
- Native PDF Engine bawaan Android OS.
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

def main():
    pkg = "com.centoa.jadwal"
    pkg_path = pathlib.Path(*pkg.split("."))
    app_title = "Jadwal Mengajar"

    # 1. Gradle Settings & Wrapper 8.7
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
        "rootProject.name = 'JadwalMengajar'\n"
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

    # 2. App Gradle
    write(ROOT / "app" / "build.gradle",
        "plugins { id 'com.android.application' }\n\n"
        "android {\n"
        f"    namespace '{pkg}'\n"
        "    compileSdk 34\n\n"
        "    defaultConfig {\n"
        f"        applicationId '{pkg}'\n"
        "        minSdk 26\n"
        "        targetSdk 34\n"
        "        versionCode 1\n"
        "        versionName '1.5'\n"
        "    }\n"
        "    buildTypes { release { minifyEnabled false } }\n"
        "    compileOptions {\n"
        "        sourceCompatibility JavaVersion.VERSION_17\n"
        "        targetCompatibility JavaVersion.VERSION_17\n"
        "    }\n"
        "}\n\n"
        "dependencies {\n"
        "    implementation 'androidx.appcompat:appcompat:1.6.1'\n"
        "    implementation 'com.google.android.material:material:1.11.0'\n"
        "    implementation 'androidx.constraintlayout:constraintlayout:2.1.4'\n"
        "    implementation 'androidx.room:room-runtime:2.6.1'\n"
        "    annotationProcessor 'androidx.room:room-compiler:2.6.1'\n"
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
        f'        android:theme="@style/Theme.Cyberpunk"{GT}\n'
        f"        {LT}activity\n"
        f'            android:name=".MainActivity"\n'
        f'            android:exported="true"{GT}\n'
        f"            {LT}intent-filter{GT}\n"
        f'                {LT}action android:name="android.intent.action.MAIN" /{GT}\n'
        f'                {LT}category android:name="android.intent.category.LAUNCHER" /{GT}\n'
        f"            {LT}/intent-filter{GT}\n"
        f"        {LT}/activity{GT}\n\n"
        f"        {LT}receiver\n"
        f'            android:name=".ScheduleWidgetProvider"\n'
        f'            android:exported="true"{GT}\n'
        f"            {LT}intent-filter{GT}\n"
        f'                {LT}action android:name="android.appwidget.action.APPWIDGET_UPDATE" /{GT}\n'
        f"            {LT}/intent-filter{GT}\n"
        f'            {LT}meta-data android:name="android.appwidget.provider" android:resource="@xml/widget_info" /{GT}\n'
        f"        {LT}/receiver{GT}\n"
        f"    {LT}/application{GT}\n"
        f"{LT}/manifest{GT}\n"
    )

    # 4. Resources
    write(ROOT / "app" / "src" / "main" / "res" / "values" / "colors.xml",
        f"{LT}?xml version=\"1.0\" encoding=\"utf-8\"?{GT}\n"
        f"{LT}resources{GT}\n"
        f"    {LT}color name=\"cyber_bg\"{GT}#070D18{LT}/color{GT}\n"
        f"    {LT}color name=\"cyber_card\"{GT}#0F2744{LT}/color{GT}\n"
        f"    {LT}color name=\"cyber_cyan\"{GT}#00D4AA{LT}/color{GT}\n"
        f"    {LT}color name=\"cyber_magenta\"{GT}#FF00FF{LT}/color{GT}\n"
        f"    {LT}color name=\"text_white\"{GT}#F8FAFC{LT}/color{GT}\n"
        f"    {LT}color name=\"text_dim\"{GT}#8EA5C8{LT}/color{GT}\n"
        f"{LT}/resources{GT}\n"
    )

    write(ROOT / "app" / "src" / "main" / "res" / "values" / "styles.xml",
        f"{LT}?xml version=\"1.0\" encoding=\"utf-8\"?{GT}\n"
        f"{LT}resources{GT}\n"
        f'    {LT}style name="Theme.Cyberpunk" parent="Theme.MaterialComponents.DayNight.NoActionBar"{GT}\n'
        f'        {LT}item name="android:windowBackground"{GT}@color/cyber_bg{LT}/item{GT}\n'
        f'        {LT}item name="android:statusBarColor"{GT}@color/cyber_bg{LT}/item{GT}\n'
        f'        {LT}item name="android:navigationBarColor"{GT}@color/cyber_bg{LT}/item{GT}\n'
        f'        {LT}item name="colorPrimary"{GT}@color/cyber_cyan{LT}/item{GT}\n'
        f'        {LT}item name="colorSecondary"{GT}@color/cyber_magenta{LT}/item{GT}\n'
        f"    {LT}/style{GT}\n"
        f"{LT}/resources{GT}\n"
    )

    write(ROOT / "app" / "src" / "main" / "res" / "values" / "strings.xml",
        f"{LT}resources{GT}{LT}string name=\"app_name\"{GT}{app_title}{LT}/string{GT}{LT}/resources{GT}"
    )

    write(ROOT / "app" / "src" / "main" / "res" / "drawable" / "ic_launcher.xml",
        f"{LT}?xml version=\"1.0\" encoding=\"utf-8\"?{GT}\n"
        f'{LT}vector xmlns:android="http://schemas.android.com/apk/res/android" android:width="108dp" android:height="108dp" android:viewportWidth="108" android:viewportHeight="108"{GT}\n'
        f'    {LT}path android:fillColor="#070D18" android:pathData="M0,0h108v108h-108z"/{GT}\n'
        f'    {LT}path android:fillColor="#00D4AA" android:pathData="M30,30h48v48h-48z"/{GT}\n'
        f'    {LT}path android:fillColor="#FF00FF" android:pathData="M44,44h20v20h-20z"/{GT}\n'
        f"{LT}/vector{GT}\n"
    )

    write(ROOT / "app" / "src" / "main" / "res" / "xml" / "widget_info.xml",
        f"{LT}?xml version=\"1.0\" encoding=\"utf-8\"?{GT}\n"
        f'{LT}appwidget-provider xmlns:android="http://schemas.android.com/apk/res/android"\n'
        f'    android:minWidth="250dp"\n'
        f'    android:minHeight="110dp"\n'
        f'    android:updatePeriodMillis="60000"\n'
        f'    android:initialLayout="@layout/widget_layout"\n'
        f'    android:resizeMode="horizontal|vertical"\n'
        f'    android:widgetCategory="home_screen" /{GT}\n'
    )

    write(ROOT / "app" / "src" / "main" / "res" / "layout" / "widget_layout.xml",
        f"{LT}?xml version=\"1.0\" encoding=\"utf-8\"?{GT}\n"
        f'{LT}LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"\n'
        f'    android:layout_width="match_parent"\n'
        f'    android:layout_height="match_parent"\n'
        f'    android:background="#0F2744"\n'
        f'    android:orientation="vertical"\n'
        f'    android:padding="14dp"{GT}\n'
        f'    {LT}TextView android:id="@+id/txt_widget_clock" android:layout_width="wrap_content" android:layout_height="wrap_content" android:text="07:30" android:textColor="#00D4AA" android:textSize="22sp" android:textStyle="bold" /{GT}\n'
        f'    {LT}TextView android:id="@+id/txt_widget_status" android:layout_width="wrap_content" android:layout_height="wrap_content" android:text="Jadwal Hari Ini: Siap Mengajar" android:textColor="#F8FAFC" android:textSize="13sp" android:layout_marginTop="4dp" /{GT}\n'
        f"{LT}/LinearLayout{GT}\n"
    )

    # 5. Activity Layout (3 Container View untuk Masing-Masing Menu)
    write(ROOT / "app" / "src" / "main" / "res" / "layout" / "activity_main.xml",
        f"{LT}?xml version=\"1.0\" encoding=\"utf-8\"?{GT}\n"
        f'{LT}RelativeLayout xmlns:android="http://schemas.android.com/apk/res/android"\n'
        f'    android:layout_width="match_parent"\n'
        f'    android:layout_height="match_parent"\n'
        f'    android:background="@color/cyber_bg"{GT}\n'
        f'    {LT}ScrollView android:layout_width="match_parent" android:layout_height="match_parent" android:layout_above="@id/bottom_nav"{GT}\n'
        f'        {LT}LinearLayout android:layout_width="match_parent" android:layout_height="wrap_content" android:orientation="vertical" android:padding="18dp"{GT}\n'
        f'            {LT}!-- VIEW 1: DASHBOARD --{GT}\n'
        f'            {LT}LinearLayout android:id="@+id/view_dashboard" android:layout_width="match_parent" android:layout_height="wrap_content" android:orientation="vertical"{GT}\n'
        f'                {LT}TextView android:id="@+id/txt_clock" android:layout_width="wrap_content" android:layout_height="wrap_content" android:text="12:00:00" android:textColor="@color/cyber_cyan" android:textSize="32sp" android:textStyle="bold" /{GT}\n'
        f'                {LT}TextView android:id="@+id/txt_profile" android:layout_width="wrap_content" android:layout_height="wrap_content" android:text="Guru: Centoa | Sekolah: SMK Cyber" android:textColor="@color/text_dim" android:textSize="14sp" android:layout_marginBottom="16dp" /{GT}\n'
        f'                {LT}LinearLayout android:layout_width="match_parent" android:layout_height="wrap_content" android:orientation="horizontal" android:weightSum="3" android:layout_marginBottom="16dp"{GT}\n'
        f'                    {LT}TextView android:layout_width="0dp" android:layout_height="wrap_content" android:layout_weight="1" android:background="@color/cyber_card" android:padding="12dp" android:gravity="center" android:text="4\\nJADWAL" android:textColor="@color/text_white" /{GT}\n'
        f'                    {LT}TextView android:layout_width="0dp" android:layout_height="wrap_content" android:layout_weight="1" android:background="@color/cyber_card" android:layout_marginStart="8dp" android:padding="12dp" android:gravity="center" android:text="4\\nKELAS" android:textColor="@color/cyber_cyan" /{GT}\n'
        f'                    {LT}TextView android:layout_width="0dp" android:layout_height="wrap_content" android:layout_weight="1" android:background="@color/cyber_card" android:layout_marginStart="8dp" android:padding="12dp" android:gravity="center" android:text="4\\nRUANG" android:textColor="@color/cyber_magenta" /{GT}\n'
        f'                {LT}/LinearLayout{GT}\n'
        f'            {LT}/LinearLayout{GT}\n'
        f'            {LT}!-- VIEW 2: DAFTAR JADWAL --{GT}\n'
        f'            {LT}LinearLayout android:id="@+id/view_jadwal" android:layout_width="match_parent" android:layout_height="wrap_content" android:orientation="vertical"{GT}\n'
        f'                {LT}TextView android:layout_width="wrap_content" android:layout_height="wrap_content" android:text="DAFTAR JADWAL LENGKAP" android:textColor="@color/cyber_cyan" android:textSize="16sp" android:textStyle="bold" android:layout_marginBottom="10dp" /{GT}\n'
        f'                {LT}LinearLayout android:id="@+id/schedule_list_container" android:layout_width="match_parent" android:layout_height="wrap_content" android:orientation="vertical" /{GT}\n'
        f'            {LT}/LinearLayout{GT}\n'
        f'            {LT}!-- VIEW 3: EXPORT PDF --{GT}\n'
        f'            {LT}LinearLayout android:id="@+id/view_export" android:layout_width="match_parent" android:layout_height="wrap_content" android:orientation="vertical" android:visibility="gone"{GT}\n'
        f'                {LT}TextView android:layout_width="wrap_content" android:layout_height="wrap_content" android:text="CETAK JADWAL KE PDF" android:textColor="@color/cyber_magenta" android:textSize="18sp" android:textStyle="bold" android:layout_marginBottom="8dp" /{GT}\n'
        f'                {LT}TextView android:layout_width="wrap_content" android:layout_height="wrap_content" android:text="Simpan format dokumen resmi A4 ke folder penyimpanan internal perangkat." android:textColor="@color/text_dim" android:textSize="13sp" android:layout_marginBottom="20dp" /{GT}\n'
        f'                {LT}Button android:id="@+id/btn_generate_pdf" android:layout_width="match_parent" android:layout_height="52dp" android:backgroundTint="@color/cyber_cyan" android:text="GENERATE PDF JADWAL" android:textColor="#070D18" android:textStyle="bold" /{GT}\n'
        f'            {LT}/LinearLayout{GT}\n'
        f'        {LT}/LinearLayout{GT}\n'
        f'    {LT}/ScrollView{GT}\n'
        f'    {LT}!-- BOTTOM NAVIGATION --{GT}\n'
        f'    {LT}LinearLayout android:id="@+id/bottom_nav" android:layout_width="match_parent" android:layout_height="62dp" android:layout_alignParentBottom="true" android:background="@color/cyber_card" android:orientation="horizontal" android:weightSum="3"{GT}\n'
        f'        {LT}TextView android:id="@+id/nav_dashboard" android:layout_width="0dp" android:layout_height="match_parent" android:layout_weight="1" android:gravity="center" android:text="DASHBOARD" android:textColor="@color/cyber_cyan" android:textStyle="bold" android:clickable="true" android:focusable="true" /{GT}\n'
        f'        {LT}TextView android:id="@+id/nav_jadwal" android:layout_width="0dp" android:layout_height="match_parent" android:layout_weight="1" android:gravity="center" android:text="JADWAL" android:textColor="@color/text_dim" android:clickable="true" android:focusable="true" /{GT}\n'
        f'        {LT}TextView android:id="@+id/nav_export" android:layout_width="0dp" android:layout_height="match_parent" android:layout_weight="1" android:gravity="center" android:text="EXPORT PDF" android:textColor="@color/text_dim" android:clickable="true" android:focusable="true" /{GT}\n'
        f'    {LT}/LinearLayout{GT}\n'
        f"{LT}/RelativeLayout{GT}\n"
    )

    # 6. Room Source Code & MainActivity Lengkap
    src_dir = ROOT / "app" / "src" / "main" / "java" / pkg_path

    # Entity
    write(src_dir / "Schedule.java",
        f"package {pkg};\n\n"
        "import androidx.room.Entity;\n"
        "import androidx.room.PrimaryKey;\n\n"
        "@Entity(tableName = \"schedules\")\n"
        "public class Schedule {\n"
        "    @PrimaryKey(autoGenerate = true)\n"
        "    public int id;\n"
        "    public String hari;\n"
        "    public String jam;\n"
        "    public String mapel;\n"
        "    public String kelas;\n"
        "    public String ruangan;\n\n"
        "    public Schedule(String hari, String jam, String mapel, String kelas, String ruangan) {\n"
        "        this.hari = hari;\n"
        "        this.jam = jam;\n"
        "        this.mapel = mapel;\n"
        "        this.kelas = kelas;\n"
        "        this.ruangan = ruangan;\n"
        "    }\n"
        "}\n"
    )

    # DAO
    write(src_dir / "ScheduleDao.java",
        f"package {pkg};\n\n"
        "import androidx.room.Dao;\n"
        "import androidx.room.Insert;\n"
        "import androidx.room.Query;\n"
        "import java.util.List;\n\n"
        "@Dao\n"
        "public interface ScheduleDao {\n"
        "    @Query(\"SELECT * FROM schedules\")\n"
        "    List<Schedule> getAll();\n\n"
        "    @Insert\n"
        "    void insertAll(Schedule... schedules);\n\n"
        "    @Query(\"SELECT COUNT(*) FROM schedules\")\n"
        "    int count();\n"
        "}\n"
    )

    # AppDatabase
    write(src_dir / "AppDatabase.java",
        f"package {pkg};\n\n"
        "import androidx.room.Database;\n"
        "import androidx.room.Room;\n"
        "import androidx.room.RoomDatabase;\n"
        "import android.content.Context;\n\n"
        "@Database(entities = {Schedule.class}, version = 1, exportSchema = false)\n"
        "public abstract class AppDatabase extends RoomDatabase {\n"
        "    public abstract ScheduleDao scheduleDao();\n"
        "    private static AppDatabase instance;\n\n"
        "    public static synchronized AppDatabase getInstance(Context context) {\n"
        "        if (instance == null) {\n"
        "            instance = Room.databaseBuilder(context.getApplicationContext(),\n"
        "                    AppDatabase.class, \"jadwal_db\")\n"
        "                    .allowMainThreadQueries()\n"
        "                    .build();\n"
        "        }\n"
        "        return instance;\n"
        "    }\n"
        "}\n"
    )

    # Widget Provider
    write(src_dir / "ScheduleWidgetProvider.java",
        f"package {pkg};\n\n"
        "import android.appwidget.AppWidgetManager;\n"
        "import android.appwidget.AppWidgetProvider;\n"
        "import android.content.Context;\n"
        "import android.widget.RemoteViews;\n"
        "import java.text.SimpleDateFormat;\n"
        "import java.util.Date;\n"
        "import java.util.Locale;\n\n"
        "public class ScheduleWidgetProvider extends AppWidgetProvider {\n"
        "    @Override\n"
        "    public void onUpdate(Context context, AppWidgetManager appWidgetManager, int[] appWidgetIds) {\n"
        "        for (int id : appWidgetIds) {\n"
        "            RemoteViews views = new RemoteViews(context.getPackageName(), R.layout.widget_layout);\n"
        "            String time = new SimpleDateFormat(\"HH:mm\", Locale.getDefault()).format(new Date());\n"
        "            views.setTextViewText(R.id.txt_widget_clock, time);\n"
        "            views.setTextViewText(R.id.txt_widget_status, \"Jadwal Aktif Hari Ini\");\n"
        "            appWidgetManager.updateAppWidget(id, views);\n"
        "        }\n"
        "    }\n"
        "}\n"
    )

    # MainActivity (Event Listener Klik & PDF Builder)
    write(src_dir / "MainActivity.java",
        f"package {pkg};\n\n"
        "import android.app.Activity;\n"
        "import android.content.Context;\n"
        "import android.graphics.Color;\n"
        "import android.graphics.Paint;\n"
        "import android.graphics.pdf.PdfDocument;\n"
        "import android.os.Bundle;\n"
        "import android.os.Handler;\n"
        "import android.os.Looper;\n"
        "import android.os.Vibrator;\n"
        "import android.view.View;\n"
        "import android.widget.Button;\n"
        "import android.widget.LinearLayout;\n"
        "import android.widget.TextView;\n"
        "import android.widget.Toast;\n"
        "import java.io.File;\n"
        "import java.io.FileOutputStream;\n"
        "import java.text.SimpleDateFormat;\n"
        "import java.util.Date;\n"
        "import java.util.List;\n"
        "import java.util.Locale;\n\n"
        "public class MainActivity extends Activity {\n"
        "    private TextView txtClock, navDashboard, navJadwal, navExport;\n"
        "    private LinearLayout viewDashboard, viewJadwal, viewExport, containerJadwal;\n"
        "    private Button btnGeneratePdf;\n"
        "    private Handler handler = new Handler(Looper.getMainLooper());\n"
        "    private Vibrator vibrator;\n\n"
        "    @Override\n"
        "    protected void onCreate(Bundle savedInstanceState) {\n"
        "        super.onCreate(savedInstanceState);\n"
        "        setContentView(R.layout.activity_main);\n\n"
        "        vibrator = (Vibrator) getSystemService(Context.VIBRATOR_SERVICE);\n"
        "        txtClock = findViewById(R.id.txt_clock);\n"
        "        navDashboard = findViewById(R.id.nav_dashboard);\n"
        "        navJadwal = findViewById(R.id.nav_jadwal);\n"
        "        navExport = findViewById(R.id.nav_export);\n"
        "        viewDashboard = findViewById(R.id.view_dashboard);\n"
        "        viewJadwal = findViewById(R.id.view_jadwal);\n"
        "        viewExport = findViewById(R.id.view_export);\n"
        "        containerJadwal = findViewById(R.id.schedule_list_container);\n"
        "        btnGeneratePdf = findViewById(R.id.btn_generate_pdf);\n\n"
        "        startClock();\n\n"
        "        AppDatabase db = AppDatabase.getInstance(this);\n"
        "        if (db.scheduleDao().count() == 0) {\n"
        "            db.scheduleDao().insertAll(\n"
        "                new Schedule(\"Senin\", \"07:30 - 09:00\", \"Pemrograman Web\", \"XII-RPL 1\", \"Lab Software\"),\n"
        "                new Schedule(\"Senin\", \"09:15 - 11:30\", \"Basis Data\", \"XI-RPL 2\", \"Lab Komputer 3\"),\n"
        "                new Schedule(\"Selasa\", \"08:00 - 10:00\", \"Sistem Operasi\", \"X-TKJ 1\", \"Ruang 12\"),\n"
        "                new Schedule(\"Rabu\", \"10:00 - 12:00\", \"Mobile App Dev\", \"XII-RPL 2\", \"Lab Inovasi\")\n"
        "            );\n"
        "        }\n\n"
        "        final List<Schedule> list = db.scheduleDao().getAll();\n"
        "        renderSchedules(list);\n"
        "        setupNavigation();\n\n"
        "        btnGeneratePdf.setOnClickListener(new View.OnClickListener() {\n"
        "            @Override\n"
        "            public void onClick(View v) {\n"
        "                vibratePhone();\n"
        "                exportToPdf(list);\n"
        "            }\n"
        "        });\n"
        "    }\n\n"
        "    private void setupNavigation() {\n"
        "        navDashboard.setOnClickListener(new View.OnClickListener() {\n"
        "            @Override\n"
        "            public void onClick(View v) {\n"
        "                vibratePhone();\n"
        "                viewDashboard.setVisibility(View.VISIBLE);\n"
        "                viewJadwal.setVisibility(View.VISIBLE);\n"
        "                viewExport.setVisibility(View.GONE);\n"
        "                updateNavColors(navDashboard);\n"
        "            }\n"
        "        });\n\n"
        "        navJadwal.setOnClickListener(new View.OnClickListener() {\n"
        "            @Override\n"
        "            public void onClick(View v) {\n"
        "                vibratePhone();\n"
        "                viewDashboard.setVisibility(View.GONE);\n"
        "                viewJadwal.setVisibility(View.VISIBLE);\n"
        "                viewExport.setVisibility(View.GONE);\n"
        "                updateNavColors(navJadwal);\n"
        "            }\n"
        "        });\n\n"
        "        navExport.setOnClickListener(new View.OnClickListener() {\n"
        "            @Override\n"
        "            public void onClick(View v) {\n"
        "                vibratePhone();\n"
        "                viewDashboard.setVisibility(View.GONE);\n"
        "                viewJadwal.setVisibility(View.GONE);\n"
        "                viewExport.setVisibility(View.VISIBLE);\n"
        "                updateNavColors(navExport);\n"
        "            }\n"
        "        });\n"
        "    }\n\n"
        "    private void updateNavColors(TextView active) {\n"
        "        navDashboard.setTextColor(Color.parseColor(\"#8EA5C8\"));\n"
        "        navJadwal.setTextColor(Color.parseColor(\"#8EA5C8\"));\n"
        "        navExport.setTextColor(Color.parseColor(\"#8EA5C8\"));\n"
        "        active.setTextColor(Color.parseColor(\"#00D4AA\"));\n"
        "    }\n\n"
        "    private void vibratePhone() {\n"
        "        if (vibrator != null) vibrator.vibrate(35);\n"
        "    }\n\n"
        "    private void exportToPdf(List<Schedule> list) {\n"
        "        PdfDocument doc = new PdfDocument();\n"
        "        PdfDocument.PageInfo pageInfo = new PdfDocument.PageInfo.Builder(595, 842, 1).create();\n"
        "        PdfDocument.Page page = doc.startPage(pageInfo);\n\n"
        "        Paint pTitle = new Paint();\n"
        "        pTitle.setColor(Color.BLACK);\n"
        "        pTitle.setTextSize(18f);\n"
        "        pTitle.setFakeBoldText(true);\n"
        "        page.getCanvas().drawText(\"JADWAL MENGAJAR GURU - CENTOA\", 40f, 60f, pTitle);\n\n"
        "        Paint pBody = new Paint();\n"
        "        pBody.setColor(Color.DKGRAY);\n"
        "        pBody.setTextSize(12f);\n"
        "        float y = 100f;\n"
        "        for (Schedule s : list) {\n"
        "            page.getCanvas().drawText(s.hari + \" (\" + s.jam + \") : \" + s.mapel + \" - \" + s.kelas + \" @ \" + s.ruangan, 40f, y, pBody);\n"
        "            y += 24f;\n"
        "        }\n\n"
        "        doc.finishPage(page);\n"
        "        try {\n"
        "            File file = new File(getExternalFilesDir(null), \"Jadwal_Mengajar.pdf\");\n"
        "            doc.writeTo(new FileOutputStream(file));\n"
        "            doc.close();\n"
        "            Toast.makeText(this, \"PDF Berhasil Dibuat: \" + file.getName(), Toast.LENGTH_LONG).show();\n"
        "        } catch (Exception e) {\n"
        "            Toast.makeText(this, \"Gagal membuat PDF: \" + e.getMessage(), Toast.LENGTH_SHORT).show();\n"
        "        }\n"
        "    }\n\n"
        "    private void startClock() {\n"
        "        handler.post(new Runnable() {\n"
        "            @Override\n"
        "            public void run() {\n"
        "                String time = new SimpleDateFormat(\"HH:mm:ss\", Locale.getDefault()).format(new Date());\n"
        "                if (txtClock != null) txtClock.setText(time);\n"
        "                handler.postDelayed(this, 1000);\n"
        "            }\n"
        "        });\n"
        "    }\n\n"
        "    private void renderSchedules(List<Schedule> list) {\n"
        "        containerJadwal.removeAllViews();\n"
        "        for (Schedule s : list) {\n"
        "            TextView item = new TextView(this);\n"
        "            item.setText(s.hari + \" | \" + s.jam + \"\\n\" + s.mapel + \" - \" + s.kelas + \" (\" + s.ruangan + \")\");\n"
        "            item.setTextColor(Color.WHITE);\n"
        "            item.setTextSize(14f);\n"
        "            item.setPadding(24, 20, 24, 20);\n"
        "            item.setBackgroundColor(Color.parseColor(\"#0F2744\"));\n"
        "            LinearLayout.LayoutParams lp = new LinearLayout.LayoutParams(\n"
        "                LinearLayout.LayoutParams.MATCH_PARENT, LinearLayout.LayoutParams.WRAP_CONTENT);\n"
        "            lp.setMargins(0, 0, 0, 16);\n"
        "            item.setLayoutParams(lp);\n"
        "            containerJadwal.addView(item);\n"
        "        }\n"
        "    }\n"
        "}\n"
    )

    print(f"[OK] Pure Native Android Project ({pkg}) berhasil dirakit!")

if __name__ == "__main__":
    main()
