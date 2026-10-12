import json
from config import client, MODEL_NAME
from resume_analyzer import analyze_resume

from pathlib import Path

RESUME_PATH = (
    Path(__file__).resolve().parent
    / "local_resumes"
    / "resume.json"
)



def load_resume_data() -> dict:
    resume_dir = RESUME_PATH.parent

    # 1. 如果没有缓存，尝试自动导入
    if not RESUME_PATH.is_file():
        files = [
            p for p in resume_dir.iterdir()
            if p.is_file()
            and p.suffix.lower() in (".pdf", ".docx")
        ] if resume_dir.is_dir() else []

        if len(files) == 0:
            raise FileNotFoundError(
                "没有找到简历，请先将 PDF 或 Word "
                "放入 local_resumes 文件夹"
            )

        if len(files) > 1:
            names = [p.name for p in files]
            raise ValueError(
                f"发现多份简历：{names}，"
                "需要用户确认使用哪一份"
            )

        # 只有一份简历，自动导入
        print(f"[Auto Import] {files[0].name}")
        import_resume(files[0].name)

    # 2. 读取结构化简历
    with open(RESUME_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    # 3. 验证数据
    if not isinstance(data, dict):
        raise ValueError("简历数据格式不正确")

    for key in ("education", "skills", "projects"):
        if not isinstance(data.get(key), list):
            raise ValueError(f"简历字段格式错误：{key}")

    return data




def search_resume(query: str) -> str:
    print("\n[Tool] search_resume 被调用")
    print(f"查询需求：{query}")

    # 自动读取简历，必要时自动导入 PDF / Word
    resume_data = load_resume_data()

    # 直接返回完整的结构化简历
    result = {
        "query": query,
        "found": True,
        "resume": resume_data
    }

    return json.dumps(
        result,
        ensure_ascii=False
    )



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
    resume_skills = load_resume_data()["skills"]

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

def import_resume(file_name: str) -> str:
    """
    导入真实简历并生成结构化数据。
    由 Agent 自主决定何时调用。
    """
    print("\n[Tool] import_resume 被调用")

    resume_dir = (
        Path(__file__).resolve().parent
        / "local_resumes"
    ).resolve()

    # 只允许读取 local_resumes 内的文件
    file_path = (resume_dir / file_name).resolve()

    if not file_path.is_relative_to(resume_dir):
        raise ValueError("不允许访问简历目录之外的文件")

    # 自动判断 PDF / Word 并调用 DeepSeek 分析
    resume_data = analyze_resume(str(file_path))

    # 保存结果
    output_path = resume_dir / "resume.json"
    output_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(
            resume_data,
            f,
            ensure_ascii=False,
            indent=2
        )

    return json.dumps({
        "status": "success",
        "message": "简历导入成功",
        "skills": resume_data["skills"],
        "project_count": len(resume_data["projects"]),
        "saved_to": str(output_path)
    }, ensure_ascii=False)

