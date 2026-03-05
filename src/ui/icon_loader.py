from PySide6.QtWidgets import QFileIconProvider
from PySide6.QtCore import QFileInfo, QSize
from PySide6.QtGui import QIcon, QPixmap

class IconLoader:
    _provider = QFileIconProvider()
    
    @staticmethod
    def get_icon(path: str) -> QIcon:
        """从文件路径获取图标，如果路径无效返回默认图标。"""
        info = QFileInfo(path)
        if info.exists():
            return IconLoader._provider.icon(info)
        # 如果文件不存在，返回一个通用的可执行文件图标或占位符
        return IconLoader._provider.icon(QFileIconProvider.IconType.File)

    @staticmethod
    def get_pixmap(path: str, size: int = 64) -> QPixmap:
        """获取指定大小的图标 Pixmap。"""
        icon = IconLoader.get_icon(path)
        return icon.pixmap(QSize(size, size))
