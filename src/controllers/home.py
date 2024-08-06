from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from core.templating import templates
from core.database import get_db
from services import match as crud, region
from validation import region as schemas


router = APIRouter()
