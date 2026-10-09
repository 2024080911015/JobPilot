import json
from config import client, MODEL_NAME

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
    keyword=query.strip().lower()
    matched_skills=[]
    for skill in RESUME_DATA['skills']:
        if keyword in skill.lower():
            matched_skills.append(skill)
    matched_projects=[]
    for project in RESUME_DATA["projects"]:
        text = (
            project["name"] + " " +
            project["description"]
        ).lower()

        if keyword in text:
            matched_projects.append(project)
    # 3. 整理查询结果
    result = {
        "query": query,
        "matched_skills": matched_skills,
        "matched_projects": matched_projects,
        "found": bool(matched_skills or matched_projects)
    }

    return json.dumps(result, ensure_ascii=False)


def analyze_jd(jd_text: str) -> str:
    """
    对 JD 做最简单的关键词检测。
    """

    print("\n[TOOL] analyze_jd 被调用")

    prompt = f"""
    你是一名专业的招聘岗位分析助手。

    请分析以下招聘 JD，提取技术技能要求。

    输出 JSON 格式，结构如下：

    {{
        "job_title": "岗位名称",
        "requirements": [
            {{
                "skill": "技术名称",
                "importance": "required",
                "evidence": "JD中对应的原文"
            }}
        ]
    }}

    1. importance 只能是 required 或 preferred。
    2. 必须掌握的技术标记为 required。
    3. 优先考虑或加分项标记为 preferred。
    4. 不允许编造 JD 中没有的要求。
    5. evidence 必须引用 JD 原文。
    6. 只返回 JSON，不要输出其他内容。

    JD内容：
    {jd_text}
"""
    response=client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role":"user",
            "content":prompt
            }
        ],
        response_format={"type":"json_object"}
    )
    content=response.choices[0].message.content
    result=json.loads(content)
    return json.dumps(result,ensure_ascii=False)

def match_job(jd_text: str) -> str:
    print("\n[Tool] match_job 被调用")

    # 第一步：使用 AI 分析 JD
    jd_result = json.loads(analyze_jd(jd_text))

    # 第二步：获取简历中的技能列表
    resume_skills = RESUME_DATA["skills"]

    matched = []
    missing = []

    # 第三步：遍历岗位要求
    for requirement in jd_result["requirements"]:

        skill = requirement["skill"]

        # 忽略大小写，进行精确匹配
        is_matched = any(
            skill.lower() == s.lower()
            for s in resume_skills
        )

        item = {
            "skill": skill,
            "importance": requirement["importance"],
            "matched": is_matched
        }

        if is_matched:
            matched.append(item)
        else:
            missing.append(item)

    # 第四步：整理结果
    result = {
        "job_title": jd_result["job_title"],
        "matched_skills": matched,
        "missing_skills": missing,
        "matched_count": len(matched),
        "missing_count": len(missing)
    }

    return json.dumps(result, ensure_ascii=False, indent=2)

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
