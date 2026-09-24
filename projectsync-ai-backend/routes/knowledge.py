from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    UploadFile,
    File
)

from fastapi.responses import FileResponse

from sqlalchemy.orm import Session

from pydantic import BaseModel

from typing import Optional

from database import SessionLocal

from models.knowledge import Knowledge

from models.project import Project

import os
import shutil


router = APIRouter(
    prefix="/api/knowledge",
    tags=["Knowledge"]
)


UPLOAD_DIR = "uploads/knowledge"

os.makedirs(
    UPLOAD_DIR,
    exist_ok=True
)


def get_db():
    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()


class KnowledgeRequest(BaseModel):
    project_id: int
    title: str
    content: str
    category: Optional[str] = None


# ---------------------------------------------------------
# CREATE KNOWLEDGE
# ---------------------------------------------------------

@router.post("/")
def create_knowledge(
    data: KnowledgeRequest,
    db: Session = Depends(get_db)
):

    project = (
        db.query(Project)
        .filter(Project.id == data.project_id)
        .first()
    )

    if not project:

        raise HTTPException(
            status_code=404,
            detail="Project not found"
        )

    knowledge = Knowledge(

        project_id=data.project_id,

        title=data.title,

        content=data.content,

        category=data.category
    )

    db.add(knowledge)

    db.commit()

    db.refresh(knowledge)

    return knowledge


# ---------------------------------------------------------
# GET ALL KNOWLEDGE
# ---------------------------------------------------------

@router.get("/")
def get_knowledge(
    db: Session = Depends(get_db)
):

    return (
        db.query(Knowledge)
        .order_by(Knowledge.id.asc())
        .all()
    )


# ---------------------------------------------------------
# SEARCH
# IMPORTANT: KEEP THIS BEFORE /{knowledge_id}
# ---------------------------------------------------------

@router.get("/search/{keyword}")
def search_knowledge(
    keyword: str,
    db: Session = Depends(get_db)
):

    results = (
        db.query(Knowledge)
        .filter(
            Knowledge.title.ilike(
                f"%{keyword}%"
            )
            |
            Knowledge.content.ilike(
                f"%{keyword}%"
            )
            |
            Knowledge.category.ilike(
                f"%{keyword}%"
            )
        )
        .order_by(
            Knowledge.id.asc()
        )
        .all()
    )

    return results


# ---------------------------------------------------------
# GET ONE KNOWLEDGE DOCUMENT
# ---------------------------------------------------------

@router.get("/{knowledge_id}")
def get_knowledge_item(
    knowledge_id: int,
    db: Session = Depends(get_db)
):

    knowledge = (
        db.query(Knowledge)
        .filter(
            Knowledge.id == knowledge_id
        )
        .first()
    )

    if not knowledge:

        raise HTTPException(
            status_code=404,
            detail="Knowledge not found"
        )

    return knowledge


# ---------------------------------------------------------
# UPDATE
# ---------------------------------------------------------

@router.put("/{knowledge_id}")
def update_knowledge(
    knowledge_id: int,
    data: KnowledgeRequest,
    db: Session = Depends(get_db)
):

    knowledge = (
        db.query(Knowledge)
        .filter(
            Knowledge.id == knowledge_id
        )
        .first()
    )

    if not knowledge:

        raise HTTPException(
            status_code=404,
            detail="Knowledge not found"
        )

    project = (
        db.query(Project)
        .filter(
            Project.id == data.project_id
        )
        .first()
    )

    if not project:

        raise HTTPException(
            status_code=404,
            detail="Project not found"
        )

    knowledge.project_id = data.project_id

    knowledge.title = data.title

    knowledge.content = data.content

    knowledge.category = data.category

    db.commit()

    db.refresh(knowledge)

    return knowledge


# ---------------------------------------------------------
# DELETE
# ---------------------------------------------------------

@router.delete("/{knowledge_id}")
def delete_knowledge(
    knowledge_id: int,
    db: Session = Depends(get_db)
):

    knowledge = (
        db.query(Knowledge)
        .filter(
            Knowledge.id == knowledge_id
        )
        .first()
    )

    if not knowledge:

        raise HTTPException(
            status_code=404,
            detail="Knowledge not found"
        )

    if (
        knowledge.file_path
        and os.path.exists(knowledge.file_path)
    ):

        os.remove(
            knowledge.file_path
        )

    db.delete(knowledge)

    db.commit()

    return {
        "message": "Knowledge deleted successfully"
    }


# ---------------------------------------------------------
# UPLOAD DOCUMENT
# ---------------------------------------------------------

@router.post("/{knowledge_id}/upload")
def upload_knowledge_file(
    knowledge_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):

    knowledge = (
        db.query(Knowledge)
        .filter(
            Knowledge.id == knowledge_id
        )
        .first()
    )

    if not knowledge:

        raise HTTPException(
            status_code=404,
            detail="Knowledge not found"
        )

    if not file.filename:

        raise HTTPException(
            status_code=400,
            detail="File name is required"
        )

    safe_filename = os.path.basename(
        file.filename
    )

    file_path = os.path.join(
        UPLOAD_DIR,
        f"{knowledge_id}_{safe_filename}"
    )

    with open(
        file_path,
        "wb"
    ) as buffer:

        shutil.copyfileobj(
            file.file,
            buffer
        )

    file_size = os.path.getsize(
        file_path
    )

    knowledge.file_name = safe_filename

    knowledge.file_path = file_path

    knowledge.file_type = (
        file.content_type
        or "application/octet-stream"
    )

    knowledge.file_size = file_size

    db.commit()

    db.refresh(knowledge)

    return {
        "message": "Document uploaded successfully",

        "knowledge_id": knowledge.id,

        "file_name": knowledge.file_name,

        "file_type": knowledge.file_type,

        "file_size": knowledge.file_size,

        "file_path": knowledge.file_path
    }


# ---------------------------------------------------------
# DOWNLOAD DOCUMENT
# ---------------------------------------------------------

@router.get("/{knowledge_id}/download")
def download_knowledge_file(
    knowledge_id: int,
    db: Session = Depends(get_db)
):

    knowledge = (
        db.query(Knowledge)
        .filter(
            Knowledge.id == knowledge_id
        )
        .first()
    )

    if not knowledge:

        raise HTTPException(
            status_code=404,
            detail="Knowledge not found"
        )

    # If an uploaded file exists
    if (
        knowledge.file_path
        and os.path.exists(
            knowledge.file_path
        )
    ):

        return FileResponse(
            path=knowledge.file_path,
            filename=knowledge.file_name,
            media_type=knowledge.file_type
            or "application/octet-stream"
        )

    # If there is no uploaded file,
    # create a text document from knowledge content
    generated_dir = "uploads/knowledge/generated"

    os.makedirs(
        generated_dir,
        exist_ok=True
    )

    generated_filename = (
        f"{knowledge.title}.txt"
    )

    generated_path = os.path.join(
        generated_dir,
        generated_filename
    )

    with open(
        generated_path,
        "w",
        encoding="utf-8"
    ) as file:

        file.write(
            knowledge.content
        )

    return FileResponse(
        path=generated_path,
        filename=generated_filename,
        media_type="text/plain"
    )


# ---------------------------------------------------------
# OPEN DOCUMENT
# ---------------------------------------------------------

@router.get("/{knowledge_id}/open")
def open_knowledge_document(
    knowledge_id: int,
    db: Session = Depends(get_db)
):

    knowledge = (
        db.query(Knowledge)
        .filter(
            Knowledge.id == knowledge_id
        )
        .first()
    )

    if not knowledge:

        raise HTTPException(
            status_code=404,
            detail="Knowledge not found"
        )

    return {
        "id": knowledge.id,

        "project_id": knowledge.project_id,

        "title": knowledge.title,

        "content": knowledge.content,

        "category": knowledge.category,

        "file_name": knowledge.file_name,

        "file_type": knowledge.file_type,

        "file_size": knowledge.file_size,

        "created_at": knowledge.created_at
    }