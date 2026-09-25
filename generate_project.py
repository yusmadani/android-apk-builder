#!/usr/bin/env python3
import sys
import base64
import re
import pathlib
import json

# Menggunakan metode LT/GT agar kebal dari penghapusan tag HTML saat Copy-Paste
BASE_APP = """import React, { useState, useEffect } from 'react';
import { SafeAreaView, View, Text, ScrollView, StyleSheet, StatusBar } from 'react-native';

export default function App() {
  const [currentTime, setCurrentTime] = useState('');

  useEffect(() => {
    const timer = setInterval(() => {
      const d = new Date();
      setCurrentTime(`\({String(d.getHours()).padStart(2, '0')}:\){String(d.getMinutes()).padStart(2, '0')}`);
    }, 1000);
    return () => clearInterval(timer);
  }, []);

  return (
    LTSafeAreaView style={styles.container}GT
      LTStatusBar barStyle="light-content" backgroundColor="#070D18" /GT
      LTView style={styles.header}GT
        LTViewGT
          LTText style={styles.headerTitle}GT__APP_TITLE__LT/TextGT
          LTText style={styles.headerSubtitle}GTPro Expo Framework • Hermes AOTLT/TextGT
        LT/ViewGT
        LTView style={styles.clockBadge}GTLTText style={styles.clockText}GT{currentTime || '00:00'}LT/TextGTLT/ViewGT
      LT/ViewGT
      LTScrollView contentContainerStyle={styles.scrollContent}GT
        LTView style={styles.card}GT
          LTText style={styles.cardHeader}GTSistem Siap DigunakanLT/TextGT
          LTText style={styles.infoText}GTMesin Expo Prebuild & Hermes Engine berjalan sempurna di 60 FPS.LT/TextGT
        LT/ViewGT
      LT/ScrollViewGT
    LT/SafeAreaViewGT
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#070D18' },
  header: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', padding: 20, backgroundColor: '#0B1424', borderBottomWidth: 1, borderColor: '#1F3454' },
  headerTitle: { fontSize: 20, fontWeight: '800', color: '#00D4AA' },
  headerSubtitle: { fontSize: 11, color: '#8EA5C8', marginTop: 2 },
  clockBadge: { backgroundColor: 'rgba(0, 212, 170, 0.12)', paddingHorizontal: 12, paddingVertical: 6, borderRadius: 8 },
  clockText: { color: '#00D4AA', fontWeight: '700' },
  scrollContent: { padding: 16 },
  card: { backgroundColor: '#0F2744', borderRadius: 18, padding: 18 },
  cardHeader: { fontSize: 16, fontWeight: '700', color: '#FFFFFF' },
  infoText: { fontSize: 13, color: '#8EA5C8', marginTop: 8 }
});
""".replace("LT", "<").replace("GT", ">")

def clean_user_jsx(code):
    if not code: return ""
    c = code.strip()
    c = re.sub(r"^```(?:javascript|jsx|tsx|js)?\s*", "", c, flags=re.IGNORECASE)
    c = re.sub(r"\s*```$", "", c)
    c = c.replace("<", "<").replace(">", ">").replace("&", "&")
    if "import React" in c and "export default" in c: return c
    return ""

def main():
    app_name = sys.argv[1] if len(sys.argv) > 1 else "ProApp"
    b64 = sys.argv[2] if len(sys.argv) > 2 else ""
    
    clean_name = re.sub(r"[^\w\s-]", "", app_name).strip() or "ProApp"
    pkg_suffix = re.sub(r"[^a-zA-Z0-9]", "", clean_name).lower() or "app"
    
    user_code = ""
    if b64:
        try:
            user_code = clean_user_jsx(base64.b64decode(b64).decode("utf-8", errors="ignore"))
        except:
            pass

    final_code = user_code if user_code else BASE_APP.replace("__APP_TITLE__", clean_name)
    
    app_file = pathlib.Path("MobileApp/App.js")
    app_file.parent.mkdir(parents=True, exist_ok=True)
    app_file.write_text(final_code, encoding="utf-8")

    app_json = pathlib.Path("MobileApp/app.json")
    if app_json.exists():
        data = json.loads(app_json.read_text())
        data["expo"]["name"] = clean_name
        data["expo"]["slug"] = pkg_suffix
        data["expo"]["android"] = {"package": f"com.pro.{pkg_suffix}"}
        app_json.write_text(json.dumps(data, indent=2))
        
    print("Injeksi App.js berhasil!")

if __name__ == "__main__":
    main()
