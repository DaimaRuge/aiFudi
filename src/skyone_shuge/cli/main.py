# SkyOne Shuge CLI
#天一阁命令行工具

import typer
from pathlib import Path
from typing import List
from ..core.config import settings

app = typer.Typer(
    name="skyone",
    help="天一阁 - 智能个人数字文献管理平台 CLI"
)


@app.command("scan")
def scan_command(
    paths: List[str] = typer.Argument(..., help="要扫描的目录路径"),
    recursive: bool = typer.Option(True, "--no-recursive", help="不递归扫描子目录"),
    extensions: str = typer.Option(None, "--ext", help="扫描的文件扩展名，逗号分隔")
):
    """扫描文档目录"""
    typer.echo(f"扫描目录: {paths}")
    typer.echo(f"递归: {recursive}")


@app.command("search")
def search_command(
    query: str = typer.Argument(..., help="搜索关键词"),
    limit: int = typer.Option(20, "-l", "--limit", help="结果数量")
):
    """搜索文档"""
    typer.echo(f"搜索: {query}")
    typer.echo(f"限制: {limit}")


@app.command("status")
def status_command():
    """查看状态"""
    typer.echo(f"📚 {settings.APP_NAME}")
    typer.echo(f"📦 版本: {settings.APP_VERSION}")
    typer.echo(f"🗂️  数据库: {settings.DATABASE_URL}")


@app.command("init")
def init_command():
    """初始化数据库"""
    from ..core.database import init_db
    
    typer.echo("🚀 初始化数据库...")
    init_db()
    typer.e!")


def main():
    """cho("✅ 完成主入口"""
    app()


if __name__ == "__main__":
    main()
