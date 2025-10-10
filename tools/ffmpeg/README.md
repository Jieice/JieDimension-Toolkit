# FFmpeg 便携版

> **目的**: 内置FFmpeg，无需系统安装

---

## 📥 下载FFmpeg

### 方法1：自动下载（推荐）

运行脚本自动下载：
```powershell
.\下载FFmpeg.ps1
```

### 方法2：手动下载

1. **访问**: https://www.gyan.dev/ffmpeg/builds/
2. **下载**: `ffmpeg-release-essentials.zip`（约100MB）
3. **解压**: 解压到此目录
4. **结构**:
   ```
   tools/ffmpeg/
   ├── bin/
   │   ├── ffmpeg.exe  ← 需要这个
   │   ├── ffplay.exe
   │   └── ffprobe.exe
   └── README.md（本文件）
   ```

---

## ✅ 安装完成检查

**应该有这个文件**:
```
tools/ffmpeg/bin/ffmpeg.exe
```

**测试**:
```powershell
.\tools\ffmpeg\bin\ffmpeg.exe -version
```

---

## 🔧 代码配置

**video_generator.py会自动检测**:
```python
# 优先使用项目内的FFmpeg
ffmpeg_path = "tools/ffmpeg/bin/ffmpeg.exe"
if os.path.exists(ffmpeg_path):
    os.environ["IMAGEIO_FFMPEG_EXE"] = ffmpeg_path
```

**无需手动配置！**

---

**下载地址**: https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip


