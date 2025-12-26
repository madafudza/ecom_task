from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import List
import csv
from io import StringIO
from datetime import datetime
from app.database import db
from app.models import UploadResponse, StudentTwoCount

router = APIRouter()


@router.post("/upload-grades", response_model=UploadResponse)
async def upload_grades(file: UploadFile = File(...)):
    """Загрузка CSV файла с оценками студентов"""
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Файл должен быть в формате CSV")

    try:
        contents = await file.read()
        decoded = contents.decode("utf-8-sig")

        first_line = decoded.split("\n")[0] if decoded else ""
        delimiter = ";" if ";" in first_line else ","

        csv_reader = csv.DictReader(StringIO(decoded), delimiter=delimiter)

        if not csv_reader.fieldnames:
            raise HTTPException(status_code=400, detail="CSV файл пустой")

        fieldnames = [f.strip() for f in csv_reader.fieldnames]
        csv_reader.fieldnames = fieldnames

        required = {"Дата", "Номер группы", "ФИО", "Оценка"}
        found = set(fieldnames)

        if not required.issubset(found):
            raise HTTPException(
                status_code=400,
                detail=f"Нужны колонки: {', '.join(required)}. Найдено: {', '.join(found)}",
            )

        records = []
        for row_num, row in enumerate(csv_reader, start=2):
            if not any(row.values()):
                continue

            try:
                date_str = row["Дата"].strip()
                parsed_date = None
                for fmt in ["%d.%m.%Y", "%Y-%m-%d", "%d/%m/%Y"]:
                    try:
                        parsed_date = datetime.strptime(date_str, fmt).date()
                        break
                    except:
                        pass
                if not parsed_date:
                    raise ValueError(f"Неверная дата: {date_str}")

                full_name = row["ФИО"].strip()
                if not full_name:
                    raise ValueError("ФИО пусто")

                group = row["Номер группы"].strip()
                if not group:
                    raise ValueError("Номер группы пуст")

                grade_str = row["Оценка"].strip()
                if not grade_str:
                    raise ValueError("Оценка пуста")

                grade = int(grade_str)
                if not 2 <= grade <= 5:
                    raise ValueError(f"Оценка {grade} должна быть от 2 до 5")

                records.append((parsed_date, group, full_name, grade))

            except Exception as e:
                raise HTTPException(
                    status_code=400, detail=f"Ошибка в строке {row_num}: {str(e)}"
                )

        if not records:
            raise HTTPException(status_code=400, detail="Нет данных для загрузки")

        await db.execute("TRUNCATE TABLE grades")

        query = "INSERT INTO grades (date, group_number, full_name, grade) VALUES ($1, $2, $3, $4)"
        await db.executemany(query, records)

        result = await db.fetchrow(
            "SELECT COUNT(DISTINCT full_name) as cnt FROM grades"
        )
        students_count = result["cnt"] if result else 0

        return UploadResponse(
            status="ok", records_loaded=len(records), students=students_count
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка сервера: {str(e)}")


@router.get("/students/more-than-3-twos", response_model=List[StudentTwoCount])
async def get_students_more_than_3_twos():
    """Студенты с > 3 двойками"""
    query = """
        SELECT full_name, COUNT(*) as count_twos
        FROM grades
        WHERE grade = 2
        GROUP BY full_name
        HAVING COUNT(*) > 3
        ORDER BY count_twos DESC, full_name
    """
    rows = await db.fetch(query)
    return [
        StudentTwoCount(full_name=r["full_name"], count_twos=r["count_twos"])
        for r in rows
    ]


@router.get("/students/less-than-5-twos", response_model=List[StudentTwoCount])
async def get_students_less_than_5_twos():
    """Студенты с < 5 двойками"""
    query = """
        SELECT full_name, COUNT(*) as count_twos
        FROM grades
        WHERE grade = 2
        GROUP BY full_name
        HAVING COUNT(*) < 5
        ORDER BY count_twos DESC, full_name
    """
    rows = await db.fetch(query)
    return [
        StudentTwoCount(full_name=r["full_name"], count_twos=r["count_twos"])
        for r in rows
    ]
