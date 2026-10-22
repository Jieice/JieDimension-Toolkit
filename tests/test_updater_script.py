"""
更新脚本生成的回归测试

背景：_create_update_script 曾用 encoding='gbk' 写 bat，而模板里含 ✓/✗（U+2713/U+2717），
导致 UnicodeEncodeError 被 install_update 的 except 吞掉、静默返回 False——
用户点"一键更新"永远失败，而且 tests/test_updater.py 只测了版本号比较，
这个 bug 因此存活了很久。

这里用真断言锁住三件事：
1. bat 能写出来，不抛编码异常
2. bat 能按 GBK 读回（cmd.exe 就是按本地代码页解析的）
3. 备份/回滚覆盖 data 和 config，而不是只有 exe（只备份 exe 会丢用户数据）
"""

import os
import sys
import tempfile
import shutil
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.updater import UpdateChecker


class TestUpdateScriptGeneration(unittest.TestCase):

    def setUp(self):
        self.checker = UpdateChecker()
        self.workdir = tempfile.mkdtemp(prefix="jdt_updater_test_")
        self.script = os.path.join(self.workdir, "update_installer.bat")
        self.temp_dir = os.path.join(self.workdir, "temp_update")
        self.target_dir = self.workdir
        self.exe_path = os.path.join(self.workdir, "JieDimension-Toolkit.exe")

    def tearDown(self):
        shutil.rmtree(self.workdir, ignore_errors=True)

    def _generate(self):
        self.checker._create_update_script(
            self.script, self.temp_dir, self.target_dir, self.exe_path
        )
        return self.script

    def test_script_is_written_without_encoding_error(self):
        """回归点：生成 bat 不能抛 UnicodeEncodeError"""
        self._generate()
        self.assertTrue(os.path.exists(self.script), "bat 未生成")
        self.assertGreater(os.path.getsize(self.script), 0, "bat 是空文件")

    def test_script_decodes_as_gbk(self):
        """cmd.exe 按本地代码页读 bat，所以必须能用 GBK 解回来"""
        self._generate()
        with open(self.script, "rb") as f:
            raw = f.read()
        try:
            text = raw.decode("gbk")
        except UnicodeDecodeError as e:
            self.fail(f"bat 不是合法 GBK，cmd 会读成乱码: {e}")
        self.assertNotIn("?", text.split("\n")[0],
                         "首行出现 ? 替换符，说明有字符被降级")

    def test_script_contains_full_update_flow(self):
        """五个关键节点缺一个，更新流程就是断的"""
        self._generate()
        with open(self.script, "rb") as f:
            text = f.read().decode("gbk")
        for marker in (":start_update", "xcopy", "backup",
                       "goto error_end", 'start ""'):
            self.assertIn(marker, text, f"更新脚本缺少关键节点: {marker}")

    def test_backup_covers_user_data(self):
        """只备份 exe 会丢用户数据：data/ 和 config/ 必须一起备份"""
        self._generate()
        with open(self.script, "rb") as f:
            text = f.read().decode("gbk")
        self.assertIn("backup\\data", text, "备份未覆盖 data 目录，更新会丢数据库")
        self.assertIn("backup\\config", text, "备份未覆盖 config 目录，更新会丢配置")

    def test_rollback_restores_user_data(self):
        """复制失败时的回滚也要还原数据，不能只还 exe"""
        self._generate()
        with open(self.script, "rb") as f:
            text = f.read().decode("gbk")
        rollback = text.split("goto error_end")[0].split("errorlevel 1")[-1]
        self.assertIn("data", rollback, "回滚分支未还原 data 目录")
        self.assertIn("config", rollback, "回滚分支未还原 config 目录")


if __name__ == "__main__":
    unittest.main(verbosity=2)
