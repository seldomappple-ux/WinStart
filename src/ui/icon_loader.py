from PySide6.QtWidgets import QFileIconProvider
from PySide6.QtCore import QFileInfo, QSize, Qt
from PySide6.QtGui import QIcon, QPixmap, QImage, QColor
import sys
import ctypes
from ctypes import wintypes
import hashlib
import os
import subprocess
import tempfile

class IconLoader:
    _provider = QFileIconProvider()
    _pixmap_cache = {}

    @staticmethod
    def _get_cache_dir() -> str:
        base = os.getenv("APPDATA") or os.path.expanduser("~")
        cache_dir = os.path.join(base, "WinStart", "icon_cache")
        os.makedirs(cache_dir, exist_ok=True)
        return cache_dir

    @staticmethod
    def _normalize_cache_path(path: str) -> str:
        return os.path.normcase(os.path.abspath(path))

    @staticmethod
    def _get_disk_cache_key(path: str, size: int) -> str | None:
        normalized_path = IconLoader._normalize_cache_path(path)
        if not os.path.exists(normalized_path):
            return None

        try:
            mtime_ns = os.stat(normalized_path).st_mtime_ns
        except OSError:
            return None

        raw_key = f"{normalized_path}|{mtime_ns}|{int(size)}"
        return hashlib.sha256(raw_key.encode("utf-8")).hexdigest()

    @staticmethod
    def _get_disk_cache_path(path: str, size: int) -> str | None:
        cache_key = IconLoader._get_disk_cache_key(path, size)
        if not cache_key:
            return None
        return os.path.join(IconLoader._get_cache_dir(), f"{cache_key}.png")

    @staticmethod
    def _load_disk_cached_pixmap(path: str, size: int) -> QPixmap | None:
        cache_path = IconLoader._get_disk_cache_path(path, size)
        if not cache_path or not os.path.exists(cache_path):
            return None

        pixmap = QPixmap(cache_path)
        if pixmap.isNull():
            try:
                os.remove(cache_path)
            except OSError:
                pass
            return None
        return pixmap

    @staticmethod
    def _write_disk_cached_pixmap(path: str, size: int, pixmap: QPixmap) -> None:
        if pixmap.isNull():
            return

        cache_path = IconLoader._get_disk_cache_path(path, size)
        if not cache_path:
            return

        try:
            pixmap.save(cache_path, "PNG")
        except Exception:
            pass
    
    @staticmethod
    def get_icon(path: str) -> QIcon:
        """从文件路径获取图标，如果路径无效返回默认图标。"""
        info = QFileInfo(path)
        if info.exists():
            return IconLoader._provider.icon(info)
        return IconLoader._provider.icon(QFileIconProvider.IconType.File)

    @staticmethod
    def resolve_shortcut(path: str) -> str:
        """解析 .lnk 快捷方式的目标路径"""
        if not path.lower().endswith('.lnk'):
            return path
            
        try:
            # 使用 VBScript 解析快捷方式，不依赖 pywin32
            vbs_script = f"""
            Set sh = CreateObject("WScript.Shell")
            Set shortcut = sh.CreateShortcut("{path}")
            WScript.Echo shortcut.TargetPath
            """
            
            # 创建临时文件
            with tempfile.NamedTemporaryFile(suffix=".vbs", delete=False, mode='w') as f:
                f.write(vbs_script)
                vbs_path = f.name
                
            # 执行脚本
            result = subprocess.check_output(['cscript', '//Nologo', vbs_path], shell=True)
            target_path = result.decode('utf-8', errors='ignore').strip()
            
            # 清理
            os.remove(vbs_path)
            
            if target_path and os.path.exists(target_path):
                return target_path
                
        except Exception:
            pass
            
        return path

    @staticmethod
    def smart_scale(pixmap: QPixmap, target_size: int) -> QPixmap:
        """智能缩放：去除透明边框并缩放内容到目标大小"""
        if pixmap.isNull():
            return pixmap
            
        image = pixmap.toImage()
        width = image.width()
        height = image.height()
        
        # 扫描非透明区域边界
        min_x, min_y = width, height
        max_x, max_y = 0, 0
        has_content = False
        
        # 快速采样扫描 (步长为2以提高性能)
        step = 1
        for y in range(0, height, step):
            for x in range(0, width, step):
                if QColor(image.pixel(x, y)).alpha() > 0:
                    has_content = True
                    min_x = min(min_x, x)
                    min_y = min(min_y, y)
                    max_x = max(max_x, x)
                    max_y = max(max_y, y)
                    
        if not has_content:
            return pixmap
            
        # 计算内容区域
        content_w = max_x - min_x + 1
        content_h = max_y - min_y + 1
        
        # 如果内容占比过小 (例如小于画布的 70%)，则进行裁剪和放大
        # 或者如果画布本身很大 (如256) 但我们要缩放到 72，且内容有边框
        
        # 计算裁剪区域
        # 增加一点 padding (5%) 以避免贴边
        padding = int(max(content_w, content_h) * 0.05)
        crop_x = max(0, min_x - padding)
        crop_y = max(0, min_y - padding)
        crop_w = min(width - crop_x, content_w + padding * 2)
        crop_h = min(height - crop_y, content_h + padding * 2)
        
        # 只有当裁剪能显著提升大小时才执行 (例如裁剪掉了 > 20% 的边框)
        if crop_w < width * 0.8 or crop_h < height * 0.8:
            cropped = image.copy(crop_x, crop_y, crop_w, crop_h)
            pixmap = QPixmap.fromImage(cropped)
            
        # 最终缩放到目标大小
        if pixmap.width() != target_size or pixmap.height() != target_size:
            pixmap = pixmap.scaled(target_size, target_size, 
                                 Qt.KeepAspectRatio, Qt.SmoothTransformation)
                                 
        return pixmap

    @staticmethod
    def get_pixmap(path: str, size: int = 64) -> QPixmap:
        """获取指定大小的图标 Pixmap，优先尝试获取高分辨率图标并进行智能缩放。"""
        cache_key = (os.path.normcase(path), int(size))
        cached = IconLoader._pixmap_cache.get(cache_key)
        if cached is not None and not cached.isNull():
            return cached

        disk_cached = IconLoader._load_disk_cached_pixmap(path, size)
        if disk_cached is not None:
            IconLoader._pixmap_cache[cache_key] = disk_cached
            return disk_cached

        real_path = path
        # 解析快捷方式
        if sys.platform == "win32" and path.lower().endswith(".lnk"):
            real_path = IconLoader.resolve_shortcut(path)
        
        pixmap = None
        
        # 尝试使用 Windows API 获取高分辨率图标 (仅限 Windows)
        if sys.platform == "win32" and real_path.lower().endswith(".exe"):
            try:
                # 尝试获取超大图标 (256x256) 以便后续裁剪
                raw_pixmap = IconLoader.get_high_res_icon_windows(real_path, 256)
                if raw_pixmap and not raw_pixmap.isNull():
                    pixmap = IconLoader.smart_scale(raw_pixmap, size)
            except Exception:
                pass

        if not pixmap or pixmap.isNull():
            # 回退到标准方法
            icon = IconLoader.get_icon(path) # 使用原始路径获取关联图标
            # 请求稍微大一点的尺寸以获得清晰度，然后智能缩放
            # 如果请求 72，Qt 可能返回 32 的居中版本。
            # 如果请求 256，Qt 可能尝试找更大的。
            raw_pixmap = icon.pixmap(QSize(256, 256))
            
            # 如果返回的是默认小尺寸 (如 32x32)，直接拉伸会模糊
            # 但 smart_scale 会处理裁剪，然后缩放
            pixmap = IconLoader.smart_scale(raw_pixmap, size)

        IconLoader._pixmap_cache[cache_key] = pixmap
        IconLoader._write_disk_cached_pixmap(path, size, pixmap)
        return pixmap

    @staticmethod
    def get_high_res_icon_windows(path: str, size: int) -> QPixmap:
        """使用 Windows API 获取高分辨率图标"""
        user32 = ctypes.windll.user32
        
        phicon = (wintypes.HICON * 1)()
        piconid = (ctypes.c_uint * 1)()
        
        # 请求指定大小
        count = user32.PrivateExtractIconsW(
            path, 0, size, size, 
            phicon, piconid, 1, 0
        )
        
        if count > 0 and phicon[0]:
            try:
                # Try modern QImage.fromHICON (Qt 6)
                img = QImage.fromHICON(phicon[0])
                if not img.isNull():
                    pixmap = QPixmap.fromImage(img)
                    user32.DestroyIcon(phicon[0])
                    return pixmap
            except AttributeError:
                pass
                
            user32.DestroyIcon(phicon[0])

        return None
