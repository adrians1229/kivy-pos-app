[app]
title = POS System
package.name = possystem  
package.domain = org.example.possystem
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json,txt
source.main = posscreen.py
version = 0.1
requirements = python3,kivy

[buildozer]
log_level = 2

[android]
minapi = 21
ndk = 25b
sdk = 31
accept_sdk_license = True
android.permissions = WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE
orientation = landscape
android.arch = armeabi-v7a, arm64-v8a
