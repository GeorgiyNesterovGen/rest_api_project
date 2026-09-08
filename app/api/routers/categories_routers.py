from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import get_category_service
from app.schemas.categories_schemas import (
    CategoryCreateSchema,
    CategorySchema,
    CategoryUpdateSchema,
)
from app.services.categories_services import CategoriesService, CategoryNotFound

router = APIRouter(prefix="/categories")


@router.get("", status_code=status.HTTP_200_OK)
def read_categories(
    categories_service: CategoriesService = Depends(get_category_service),
) -> list[CategorySchema]:

    return categories_service.lists_categories()


@router.post("", status_code=status.HTTP_201_CREATED)
def create_categories(
    payload: CategoryCreateSchema,
    categories_service: CategoriesService = Depends(get_category_service),
) -> CategorySchema:

    return categories_service.create_category(category_create=payload)


@router.patch("/{category_id}", status_code=status.HTTP_200_OK)
def update_category(
    category_id: str,
    payload: CategoryUpdateSchema,
    categories_service: CategoriesService = Depends(get_category_service),
):
    try:
        return categories_service.update_category(
            category_id=category_id, category_update=payload
        )
    except CategoryNotFound:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(
    category_id: str,
    categories_service: CategoriesService = Depends(get_category_service),
):

    try:
        return categories_service.category_delete(category_id=category_id)
    except CategoryNotFound:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
