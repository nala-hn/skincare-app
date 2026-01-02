from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from ...database import models, session
from ...utils.cloudinary_helper import upload_image_to_cloud
from .auth import get_current_user

router = APIRouter(prefix="/skin-logs", tags=["Skin Logs"])

@router.post("/upload")
async def upload_skin_photo(
    file: UploadFile = File(...),
    db: Session = Depends(session.get_db),
    current_user: models.User = Depends(get_current_user)
):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File harus berupa gambar (jpg/png)")

    url = upload_image_to_cloud(file.file)
    
    if not url:
        raise HTTPException(status_code=500, detail="Gagal menyimpan gambar ke cloud storage")

    new_log = models.SkinLog(
        user_id=current_user.id,
        photo_url=url,
        ai_analysis_result={"status": "waiting_analysis"}
    )
    
    db.add(new_log)
    db.commit()
    db.refresh(new_log)

    return {
        "status": "success",
        "photo_url": url,
        "log_id": new_log.id
    }