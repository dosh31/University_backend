from django.shortcuts import render

specialists = [
    {
        "id": 1,
        "name": "Сурдоперевод",
        "description": "Обеспечение учебного процесса квалифицированными специалистами по сурдопереводу.",
        "image": "http://localhost:9000/images/1.png"
    },
    {
        "id": 2,
        "name": "Сурдотехника и ТСО",
        "description": "Настройка и обслуживание ТСО и сурдоакустических систем.",
        "image": "http://localhost:9000/images/2.png"
    },
    {
        "id": 3,
        "name": "Сурдолог",
        "description": "Занятия по развитию слухо-речевого восприятия и улучшению коммуникативных навыков.",
        "image": "http://localhost:9000/images/3.png"
    },
    {
        "id": 4,
        "name": "Психолог",
        "description": "Консультирование для поддержки психологического состояния и эмоциональной устойчивости.",
        "image": "http://localhost:9000/images/4.png"
    },
    {
        "id": 5,
        "name": "Тьютор",
        "description": "Индивидуальное консультирование по техническим дисциплинам.",
        "image": "http://localhost:9000/images/5.png"
    },
    {
        "id": 6,
        "name": "Логопед",
        "description": "Сопровождение лиц с особыми образовательными потребностями: развитие речи, улучшение фонетико-фонематических и лексико-грамматических навыков.",
        "image": "http://localhost:9000/images/6.png"
    }
]

draft_lecture = {
    "id": 123,
    "status": "Черновик",
    "date_created": "12 сентября 2024г",
    "room": "524гз",
    "date": "24 сентября 12:00",
    "specialists": [
        {
            "id": 1,
            "value": "Прийти на пол часа раньше"
        },
        {
            "id": 2,
            "value": "Задержаться на паре"
        },
        {
            "id": 3,
            "value": "Прийти на пол часа раньше"
        }
    ]
}


def getSpecialistById(specialist_id):
    for specialist in specialists:
        if specialist["id"] == specialist_id:
            return specialist


def getSpecialists():
    return specialists


def searchSpecialists(specialist_name):
    res = []

    for specialist in specialists:
        if specialist_name.lower() in specialist["name"].lower():
            res.append(specialist)

    return res


def getDraftLecture():
    return draft_lecture


def getLectureById(lecture_id):
    return draft_lecture


def index(request):
    specialist_name = request.GET.get("specialist_name", "")
    specialists = searchSpecialists(specialist_name) if specialist_name else getSpecialists()
    draft_lecture = getDraftLecture()

    context = {
        "specialists": specialists,
        "specialist_name": specialist_name,
        "specialists_count": len(draft_lecture["specialists"]),
        "draft_lecture": draft_lecture
    }

    return render(request, "home_page.html", context)


def specialist(request, specialist_id):
    context = {
        "id": specialist_id,
        "specialist": getSpecialistById(specialist_id),
    }

    return render(request, "specialist_page.html", context)


def lecture(request, lecture_id):
    lecture = getLectureById(lecture_id)
    specialists = [
        {**getSpecialistById(specialist["id"]), "value": specialist["value"]}
        for specialist in lecture["specialists"]
    ]

    context = {
        "lecture": lecture,
        "specialists": specialists
    }

    return render(request, "lecture_page.html", context)
