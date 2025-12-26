from pydantic import BaseModel, field_validator


class GradeRecord(BaseModel):
    """Модель для валидации одной записи об успеваемости"""

    date: str
    group_number: str
    full_name: str
    grade: int

    @field_validator("grade")
    @classmethod
    def validate_grade(cls, v):
        if not isinstance(v, int) or v < 2 or v > 5:
            raise ValueError("Оценка должна быть от 2 до 5")
        return v

    @field_validator("full_name")
    @classmethod
    def validate_full_name(cls, v):
        if not v or not v.strip():
            raise ValueError("ФИО не может быть пустым")
        return v.strip()

    @field_validator("group_number")
    @classmethod
    def validate_group_number(cls, v):
        if not v or not v.strip():
            raise ValueError("Номер группы не может быть пустым")
        return v.strip()


class UploadResponse(BaseModel):
    status: str
    records_loaded: int
    students: int


class StudentTwoCount(BaseModel):
    full_name: str
    count_twos: int
