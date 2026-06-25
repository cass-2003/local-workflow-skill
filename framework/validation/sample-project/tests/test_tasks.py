"""tasks 模块测试。REQ-002 的测试当前会失败（filter_by_status 未实现）。"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
import tasks


def setup_function(_):
    tasks._TASKS.clear()
    tasks._NEXT_ID = 1


def test_add_and_list():            # REQ-001（已验收）
    tasks.add_task("a")
    tasks.add_task("b")
    assert len(tasks.list_tasks()) == 2


def test_mark_done():               # REQ-001（已验收）
    t = tasks.add_task("a")
    tasks.mark_done(t["id"])
    assert tasks.list_tasks()[0]["status"] == "done"


def test_filter_by_status():        # REQ-002（待实现）
    tasks.add_task("a")
    t = tasks.add_task("b")
    tasks.mark_done(t["id"])
    assert [x["title"] for x in tasks.filter_by_status("done")] == ["b"]
    assert [x["title"] for x in tasks.filter_by_status("open")] == ["a"]
