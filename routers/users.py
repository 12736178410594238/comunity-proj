"""
사용자 라우터 - 사용자 정보 조회/수정
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.user import User
from app.schemas.user import UserResponse, UserUpdate
from app.services.auth import get_current_user, get_admin_user

router = APIRouter(prefix="/api/users", tags=["사용자"])

@router.get("/", response_model=List[UserResponse])
async def get_users(
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)  # 관리자만
):
    """
    사용자 목록 조회 (관리자 전용)
    """
    users = db.query(User).offset(skip).limit(limit).all()
    return users

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, db: Session = Depends(get_db)):
    """
    특정 사용자 정보 조회
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="사용자를 찾을 수 없습니다"
        )
    return user

@router.put("/me", response_model=UserResponse)
async def update_me(
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    내 정보 수정
    """
    # 업데이트할 필드만 변경
    if user_update.nickname is not None:
        current_user.nickname = user_update.nickname
    if user_update.bio is not None:
        current_user.bio = user_update.bio
    if user_update.profile_image is not None:
        current_user.profile_image = user_update.profile_image
    
    db.commit()
    db.refresh(current_user)
    
    return current_user

@router.delete("/me")
async def delete_me(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    회원 탈퇴
    """
    # 실제로는 soft delete (is_active = False)를 권장
    current_user.is_active = False
    db.commit()
    
    return {"message": "회원 탈퇴가 완료되었습니다"}