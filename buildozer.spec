[app]
title = POS System
package.name = possystem
package.domain = org.example.possystem
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json,txt

version = 0.1
requirements = python3,kivy,android,json,datetime

[buildozer]
log_level = 2
warn_on_root = 1

[android]
minapi = 21
ndk = 25b
sdk = 31
accept_sdk_license = True

# Permissions
android.permissions = WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE

# Orientation
orientation = landscape

# Icon (optional - you can add your own icon)
# icon.filename = %(source.dir)s/icon.png

[android.gradle_dependencies]
# Add any additional gradle dependencies here

[android.arch]
armeabi-v7a, arm64-v8a