from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from typing import List, Optional
from sqlalchemy.orm import Session
from database import get_db
import models, schemas, oauth2
from sqlalchemy import func


router = APIRouter(
    prefix='/posts', 
    tags=["Posts"] 
)

@router.get("/", response_model=List[schemas.PostOut])
def get_posts(db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user), limit: int = 10, skip: int = 0, search: Optional[str] = ""):
    # print(limit)
    # results = db.query(models.Post).join(models.Vote mo)
    # print(results)

    # would only show posts for a given user
    # posts = db.query(models.Post).filter(models.Post.owner_id == current_user.id).all() 
    # if len(posts) == 0:
    #     raise HTTPException(status_code=status.HTTP_40 4_NOT_FOUND,
    #                     detail=f"no posts with given owner_id: {str(current_user.id)}")

    posts = db.query(models.Post, func.count(models.Vote.post_id).label("votes")).join(
        models.Vote, models.Vote.post_id == models.Post.id, isouter=True).group_by(models.Post.id).filter(models.Post.title.contains(search)).limit(limit).offset(skip).all()
    # print(posts)
    return posts

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.Post)
def createposts(
    post: schemas.PostCreate, 
    db: Session = Depends(get_db), 
    current_user: int = Depends(oauth2.get_current_user)): 
        new_post = models.Post(owner_id=current_user.id, **post.dict())
        db.add(new_post)
        db.commit()
        db.refresh(new_post)
        print(current_user.email)
        return new_post

@router.get("/{id}", response_model=schemas.PostOut)
def get_post(id: int, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    # post = db.query(models.Post).filter(models.Post.id == id).first()

    post = db.query(models.Post, func.count(models.Vote.post_id).label("votes")).join(
        models.Vote, models.Vote.post_id == models.Post.id, isouter=True).group_by(models.Post.id).filter(models.Post.id == id).first()
    
    
    if not post: 
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"post with given id: {str(id)} is not in our database")
    return post


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    
    post_query = db.query(models.Post).filter(models.Post.id == id)
    
    post = post_query.first()
    
    if post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"post with given id: {str(id)} is not in our database")
    if post.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                        detail=f"not authorized to alter another users post")
    
    
    post_query.delete(synchronize_session=False)
    db.commit()

@router.put("/{id}", response_model=schemas.Post)
def update_posts(id:int, updated_post: schemas.PostCreate, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    post_query = db.query(models.Post).filter(models.Post.id == id)
    post = post_query.first()
    
    
    if post == None: 
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"post with given id: {str(id)} is not in our database")
    if post.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                        detail=f"not authorized to alter another users post")
    
    post_query.update(
        updated_post.dict(),
        synchronize_session=False
        )
    db.commit()

    return post_query.first()