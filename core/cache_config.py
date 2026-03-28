"""
FetchRouter Cache & Config - 缓存和配置管理
"""

import json
import time
import hashlib
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict


@dataclass
class CacheEntry:
    """缓存条目"""
    url: str
    content: Dict[str, Any]
    timestamp: float
    ttl: int  # 过期时间（秒）

    def is_expired(self) -> bool:
        return time.time() - self.timestamp > self.ttl


class CacheManager:
    """缓存管理器"""

    def __init__(self, cache_dir: Optional[str] = None, default_ttl: int = 300):
        self.cache_dir = Path(cache_dir or "~/.claude/skills/fetchrouter/cache").expanduser()
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.default_ttl = default_ttl
        self.memory_cache: Dict[str, CacheEntry] = {}

    def _get_cache_key(self, url: str) -> str:
        """生成缓存键"""
        return hashlib.md5(url.encode()).hexdigest()

    def _get_cache_file(self, key: str) -> Path:
        """获取缓存文件路径"""
        return self.cache_dir / f"{key}.json"

    def get(self, url: str) -> Optional[Dict[str, Any]]:
        """
        获取缓存内容
        """
        key = self._get_cache_key(url)

        # 先查内存缓存
        if key in self.memory_cache:
            entry = self.memory_cache[key]
            if not entry.is_expired():
                return entry.content
            else:
                del self.memory_cache[key]

        # 再查文件缓存
        cache_file = self._get_cache_file(key)
        if cache_file.exists():
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    entry = CacheEntry(**data)

                if not entry.is_expired():
                    # 放入内存缓存
                    self.memory_cache[key] = entry
                    return entry.content
                else:
                    # 删除过期缓存
                    cache_file.unlink()
            except Exception:
                pass

        return None

    def set(self, url: str, content: Dict[str, Any], ttl: Optional[int] = None):
        """
        设置缓存
        """
        key = self._get_cache_key(url)
        ttl = ttl or self.default_ttl

        entry = CacheEntry(
            url=url,
            content=content,
            timestamp=time.time(),
            ttl=ttl
        )

        # 写入内存缓存
        self.memory_cache[key] = entry

        # 写入文件缓存
        cache_file = self._get_cache_file(key)
        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(asdict(entry), f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"缓存写入失败: {e}")

    def clear(self):
        """
        清空所有缓存
        """
        self.memory_cache.clear()

        # 删除所有缓存文件
        for cache_file in self.cache_dir.glob("*.json"):
            try:
                cache_file.unlink()
            except:
                pass

    def clean_expired(self):
        """
        清理过期缓存
        """
        # 清理内存缓存
        expired_keys = [
            key for key, entry in self.memory_cache.items()
            if entry.is_expired()
        ]
        for key in expired_keys:
            del self.memory_cache[key]

        # 清理文件缓存
        for cache_file in self.cache_dir.glob("*.json"):
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    entry = CacheEntry(**data)

                if entry.is_expired():
                    cache_file.unlink()
            except:
                pass

    def get_stats(self) -> Dict[str, Any]:
        """获取缓存统计"""
        memory_count = len(self.memory_cache)
        disk_count = len(list(self.cache_dir.glob("*.json")))

        total_size = sum(
            f.stat().st_size
            for f in self.cache_dir.glob("*.json")
        )

        return {
            "memory_entries": memory_count,
            "disk_entries": disk_count,
            "total_size_mb": round(total_size / 1024 / 1024, 2)
        }


class ConfigManager:
    """配置管理器"""

    DEFAULT_CONFIG = {
        "cache-duration": 300,
        "default-output": "markdown",
        "max-content-length": 8000,
        "timeout": 30,
        "parallel": 3,
        "auto-detect-url": True,
        "save-directory": str(Path.home() / "Downloads"),
    }

    def __init__(self, config_dir: Optional[str] = None):
        self.config_dir = Path(config_dir or "~/.claude/skills/fetchrouter/config").expanduser()
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.config_file = self.config_dir / "settings.json"
        self._config = self.load()

    def load(self) -> Dict[str, Any]:
        """加载配置"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                    # 合并默认配置和用户配置
                    config = self.DEFAULT_CONFIG.copy()
                    config.update(user_config)
                    return config
            except:
                pass
        return self.DEFAULT_CONFIG.copy()

    def save(self):
        """保存配置"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self._config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"配置保存失败: {e}")

    def get(self, key: str, default=None):
        """获取配置项"""
        return self._config.get(key, default)

    def set(self, key: str, value):
        """设置配置项"""
        if key in self.DEFAULT_CONFIG:
            # 类型转换
            default_type = type(self.DEFAULT_CONFIG[key])
            if default_type == bool and isinstance(value, str):
                value = value.lower() in ('true', 'yes', '1', 'on')
            else:
                try:
                    value = default_type(value)
                except:
                    pass

            self._config[key] = value
            self.save()
            return True
        return False

    def reset(self):
        """重置为默认配置"""
        self._config = self.DEFAULT_CONFIG.copy()
        self.save()

    def list(self) -> Dict[str, Any]:
        """列出所有配置"""
        return self._config.copy()


# 全局实例
cache = CacheManager()
config = ConfigManager()
