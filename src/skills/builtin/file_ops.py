"""
File Operations Skill
Read, write, and manipulate files.
"""
from pathlib import Path
from typing import Optional
from ..base import Skill, SkillMetadata, SkillParameter, SkillResult


class FileOpsSkill(Skill):
    """File operations skill."""
    
    def get_metadata(self) -> SkillMetadata:
        return SkillMetadata(
            name="file_ops",
            description="Read, write, and get information about files",
            category="File System",
            parameters=[
                SkillParameter(
                    name="operation",
                    type="str",
                    description="Operation to perform: 'read', 'write', 'append', 'exists', 'size', 'list_dir'",
                    required=True
                ),
                SkillParameter(
                    name="path",
                    type="str",
                    description="Path to the file or directory",
                    required=True
                ),
                SkillParameter(
                    name="content",
                    type="str",
                    description="Content to write (for write/append operations)",
                    required=False
                )
            ],
            returns="Result of the file operation"
        )
    
    def execute(self, operation: str, path: str, content: Optional[str] = None) -> SkillResult:
        """Execute file operation."""
        try:
            file_path = Path(path)
            
            if operation == "read":
                if not file_path.exists():
                    return SkillResult(success=False, error=f"File not found: {path}")
                
                text = file_path.read_text(encoding="utf-8")
                return SkillResult(
                    success=True,
                    data=text,
                    metadata={"path": str(file_path), "size": len(text)}
                )
            
            elif operation == "write":
                if content is None:
                    return SkillResult(success=False, error="Content is required for write operation")
                
                file_path.parent.mkdir(parents=True, exist_ok=True)
                file_path.write_text(content, encoding="utf-8")
                return SkillResult(
                    success=True,
                    data=f"Wrote {len(content)} characters to {path}",
                    metadata={"path": str(file_path), "size": len(content)}
                )
            
            elif operation == "append":
                if content is None:
                    return SkillResult(success=False, error="Content is required for append operation")
                
                file_path.parent.mkdir(parents=True, exist_ok=True)
                with open(file_path, "a", encoding="utf-8") as f:
                    f.write(content)
                return SkillResult(
                    success=True,
                    data=f"Appended {len(content)} characters to {path}",
                    metadata={"path": str(file_path)}
                )
            
            elif operation == "exists":
                exists = file_path.exists()
                return SkillResult(
                    success=True,
                    data=exists,
                    metadata={"path": str(file_path)}
                )
            
            elif operation == "size":
                if not file_path.exists():
                    return SkillResult(success=False, error=f"File not found: {path}")
                
                size = file_path.stat().st_size
                return SkillResult(
                    success=True,
                    data=size,
                    metadata={"path": str(file_path), "size_bytes": size}
                )
            
            elif operation == "list_dir":
                if not file_path.exists():
                    return SkillResult(success=False, error=f"Directory not found: {path}")
                
                if not file_path.is_dir():
                    return SkillResult(success=False, error=f"Not a directory: {path}")
                
                items = [item.name for item in file_path.iterdir()]
                return SkillResult(
                    success=True,
                    data=items,
                    metadata={"path": str(file_path), "count": len(items)}
                )
            
            else:
                return SkillResult(
                    success=False,
                    error=f"Unknown operation: {operation}"
                )
        
        except Exception as e:
            return SkillResult(
                success=False,
                error=f"File operation failed: {str(e)}"
            )
