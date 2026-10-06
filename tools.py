import json


RESUME_DATA = {
    "skills": [
        "C++",
        "Python",
        "Flask",
        "SQLAlchemy",
        "SQLite",
        "PyTorch",
        "计算机网络"
    ],

    "projects": [
        {
            "name": "校园社交推荐平台",
            "description": (
                "基于 Flask 和 SQLAlchemy 实现校园社交平台后端，"
                "使用 GNN 学习用户 embedding，"
                "结合余弦相似度、用户画像和共同关注进行推荐。"
            )
        },
        {
            "name": "UE5 游戏项目",
            "description": (
                "使用 Unreal Engine 5 和 C++ 开发校园悬疑游戏，"
                "实现角色控制及交互功能。"
            )
        }
    ]
}

def search_resume(query:str)->str:
    print(f"\n[Tool]search_resume被调用")
    print(f"参数为{query}")
    return json.dumps(
        RESUME_DATA,
        ensure_ascii=False
    )


def analyze_jd(jd_text: str) -> str:
    """
    对 JD 做最简单的关键词检测。
    """

    print("\n[TOOL] analyze_jd 被调用")

    keywords = [
        "C++",
        "Python",
        "Java",
        "Flask",
        "MySQL",
        "Redis",
        "Linux",
        "TCP",
        "网络",
        "数据库",
        "算法",
        "AI",
        "Agent"
    ]

    found = []

    for keyword in keywords:
        if keyword.lower() in jd_text.lower():
            found.append(keyword)

    result = {
        "detected_skills": found,
        "original_jd": jd_text
    }

    return json.dumps(
        result,
        ensure_ascii=False
    )

def save_interview_note(note: str) -> str:
    """
    保存面试准备笔记。
    """

    print("\n[TOOL] save_interview_note 被调用")

    with open(
        "interview_notes.txt",
        "a",
        encoding="utf-8"
    ) as f:
        f.write(note + "\n")

    return "面试笔记保存成功"
