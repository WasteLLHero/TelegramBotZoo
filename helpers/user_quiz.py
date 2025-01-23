async def user_quiz_string_frtomatter(data: dict) -> str:
    result = "Результаты викторины:\n"
    for entry in data:
        result += f"Пользователь: {entry['telegramUser']}\n"
        result += f"Предложенное животное: {entry['suggested_animal']}\n"
        if entry['reasoning']:
            result += "Причины выбора:\n"
            for key, value in entry['reasoning'].items():
                result += f"  - {key}: {value}\n"
        if entry['care_recommendations']:
            result += "Рекомендации по уходу:\n"
            for key, value in entry['care_recommendations'].items():
                result += f"  - {key}: {value}\n"
        if entry['answers']:
            result += "Ответы на вопросы:\n"
            for answer in entry['answers']:
                result += f"  - {answer['question']}: {answer['answer']}\n"
        result += "\n"
    return result