from pathlib import Path
import sys
import pymupdf
from docx import Document
from docx.table import Table
from docx.text.paragraph import Paragraph

def extract_pdf_text(file_path:str)->str:
    path=Path(file_path)
    if not path.is_file:
        raise FileNotFoundError(f"文件{path}不存在")
    if path.suffix.lower()!=".pdf":
        raise ValueError("仅支持pdf文件")
    
    with pymupdf.open(str(path)) as pdf:
        if pdf.needs_pass:
            raise ValueError("PDF 已加密，需要密码")
        pages=[]
        for page in pdf:
            text=page.get_text("text",sort=True)
            pages.append(text)
    result = "\n".join(pages).strip()

    if not result:
        raise ValueError("未提取到文字，可能是扫描版 PDF")

    return result


def extract_docx_text(file_path: str) -> str:
    path = Path(file_path)

    if not path.is_file():
        raise FileNotFoundError(f"文件不存在：{path}")

    if path.suffix.lower() != ".docx":
        raise ValueError("仅支持 .docx 格式")

    # 打开 Word 文档
    doc = Document(str(path))
    contents = []

    # 按文档中的顺序读取段落和表格
    for block in doc.iter_inner_content():

        if isinstance(block, Paragraph):
            text = block.text.strip()

            if text:
                contents.append(text)

        elif isinstance(block, Table):
            for row in block.rows:
                cells = [
                    cell.text.strip()
                    for cell in row.cells
                ]

                line = " | ".join(
                    cell for cell in cells if cell
                )

                if line:
                    contents.append(line)

    result = "\n".join(contents).strip()

    if not result:
        raise ValueError("Word 文档中没有提取到文字")

    return result

def extract_resume_text(file_path: str) -> str:
    suffix = Path(file_path).suffix.lower()

    if suffix == ".pdf":
        return extract_pdf_text(file_path)

    elif suffix == ".docx":
        return extract_docx_text(file_path)

    else:
        raise ValueError("不支持的文件格式")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("用法：python resume_parser.py 简历路径")
        sys.exit(1)

    text = extract_resume_text(sys.argv[1])

    print(f"成功提取 {len(text)} 个字符")
    print("前 500 个字符：")
    print(text[:500])

        
        
