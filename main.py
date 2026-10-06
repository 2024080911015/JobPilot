import json

from config import client, MODEL_NAME
from tools import (
    search_resume,
    analyze_jd,
    save_interview_note,
)


TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "search_resume",
            "description": (
                "搜索用户的个人简历、技术能力和项目经历。"
                "当你需要了解用户会什么技术、做过什么项目时使用。"
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "需要搜索的简历内容"
                    }
                },
                "required": ["query"]
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "analyze_jd",
            "description": (
                "分析招聘岗位 JD，提取其中需要的技术能力。"
                "遇到岗位描述或招聘要求时使用。"
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "jd_text": {
                        "type": "string",
                        "description": "完整的岗位 JD"
                    }
                },
                "required": ["jd_text"]
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "save_interview_note",
            "description": (
                "把重要的面试准备内容保存到用户的学习笔记中。"
                "只有用户明确要求保存时才调用。"
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "note": {
                        "type": "string",
                        "description": "需要保存的笔记内容"
                    }
                },
                "required": ["note"]
            }
        }
    }
]

##建立tools名称到函数的映射
TOOL_FUNCTIONS = {
    "search_resume": search_resume,
    "analyze_jd": analyze_jd,
    "save_interview_note": save_interview_note,
}

SYSTEM_PROMPT = """
你是 JobPilot，一个帮助用户进行求职和面试准备的 AI Agent。

你可以使用工具完成任务。

规则：

1. 如果问题涉及用户自己的简历、技术能力或项目经历，
   应优先使用 search_resume 获取真实信息。

2. 如果用户提供招聘岗位 JD，
   应使用 analyze_jd 分析岗位需求。

3. 只有用户明确要求保存内容时，
   才允许调用 save_interview_note。

4. 不要编造用户不存在的项目经历。

5. 工具执行后，根据工具结果继续完成任务。
"""

messages=[
        {
            "role":"system",
            "content":SYSTEM_PROMPT
        }
    ]
def run_agent(user_input:str)->str:
    messages.append(
        {
            "role":"user",
            "content":user_input
        }
    )

    while True:
        response=client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            tools=TOOLS,
            tool_choice="auto"
        )

        message=response.choices[0].message

        messages.append(
            message.model_dump(exclude_none=True)
        )

        if not message.tool_calls:
            return message.content

        for tool_call in message.tool_calls:
            tool_name = tool_call.function.name

            arguments = json.loads(
                tool_call.function.arguments
            )

            print("\n============================")
            print(f"Agent 决定调用工具：{tool_name}")
            print(f"参数：{arguments}")
            print("============================")

            # 找到真正的 Python 函数
            function = TOOL_FUNCTIONS.get(tool_name)

            if function is None:
                tool_result = f"不存在工具：{tool_name}"

            else:
                try:
                    tool_result = function(**arguments)

                except Exception as e:
                    tool_result = f"工具执行失败：{str(e)}"
             # 把工具运行结果返回给 LLM
            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": str(tool_result)
                }
            )


if __name__ == "__main__":

    print("JobPilot Agent 已启动")
    print("输入 exit 退出")

    while True:

        user_input = input("\n你：")

        if user_input.lower() == "exit":
            break

        try:
            answer = run_agent(user_input)

            print("\nJobPilot：")
            print(answer)

        except Exception as e:

            print("\n程序执行失败：")
            print(e)
