"""极简任务清单核心。样板项目，用于 dogfood 四态工作流框架。"""

# 任务用 dict 表示：{"id": int, "title": str, "status": "open"|"done"}
_TASKS = []
_NEXT_ID = 1


def add_task(title):
    """新增一个 open 任务，返回任务 dict。"""
    global _NEXT_ID
    task = {"id": _NEXT_ID, "title": title, "status": "open"}
    _TASKS.append(task)
    _NEXT_ID += 1
    return task


def mark_done(task_id):
    """把指定任务标记为 done；找不到抛 KeyError。"""
    for t in _TASKS:
        if t["id"] == task_id:
            t["status"] = "done"
            return t
    raise KeyError(f"no task with id {task_id}")


def list_tasks():
    """返回全部任务（副本）。"""
    return list(_TASKS)


# REQ-002：按状态过滤任务 —— 尚未实现（dogfood 要落地的需求）
