# 1. Tulis payload.json dari bot
      - name: Create payload.json
        shell: python
        env:
          PAYLOAD_DATA: ${{ toJson(github.event.client_payload) }}
        run: |
          import os, json
          data = json.loads(os.environ.get("PAYLOAD_DATA", "{}"))
          with open("payload.json", "w", encoding="utf-8") as f:
              json.dump(data, f, ensure_ascii=False, indent=2)

      # 2. Jalankan Generator Proyek
      - name: Run Project Generator
        run: python generate_project.py

      # 3. Setup Gradle Wrapper & Build APK di dalam folder project/
      - name: Build APK with Gradle
        run: |
          cd project
          gradle wrapper --gradle-version 8.7
          chmod +x gradlew
          ./gradlew assembleDebug -Pandroid.useAndroidX=true -Pandroid.enableJetifier=true --stacktrace 2>&1 | tee ../build_output.log
