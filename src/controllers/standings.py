from fastapi import APIRouter, Depends, HTTPException, Request

router = APIRouter()


def plus(a, b):
    return a + b
