import os


class ConfigLoader:
    def __init__(self):
        pass

    def load_app_info(self):
        """加载同目录下的app info文件"""
        app_info_path = os.path.join(os.path.dirname(__file__), "app_info.txt")
        if os.path.exists(app_info_path):
            try:
                with open(app_info_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    if len(lines) >= 2:
                        app_id = lines[0].strip()
                        app_secret = lines[1].strip()
                        if app_id and app_secret:
                            return {
                                'app_id': app_id,
                                'app_secret': app_secret
                            }
            except Exception as e:
                print(f"加载app_info.txt失败: {e}")
        return None