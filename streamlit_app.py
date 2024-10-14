import streamlit as st
import aiohttp
import asyncio
import random
import pandas as pd
import matplotlib.pyplot as plt

# URL API HH
API_URL = "https://api.hh.ru/vacancies"

# Заголовки для запросов (User-Agent)
HEADERS = {'User-Agent': 'Mozilla/5.0'}

# Асинхронная функция для получения данных с hh.ru
async def get_hh_vacancies_async(session, region_id, position, experience):
    await asyncio.sleep(random.uniform(2, 5))  # Случайная задержка

    params = {
        "text": position,
        "area": region_id,
        "experience": experience,
        "per_page": 100  # Количество вакансий на странице
    }

    async with session.get(API_URL, params=params, headers=HEADERS) as response:
        if response.status == 200:
            data = await response.json()
            return data['found']
        else:
            return None


# Функция для получения данных по всем регионам, должностям и уровням
async def get_all_vacancies():
    regions = {'Москва': 1, 'Томск': 1203, 'Санкт-Петербург': 2}
    positions = ['Data Analyst', 'Data Scientist', 'Data Engineer']
    levels = ['noExperience', 'between1And3', 'between3And6']

    async with aiohttp.ClientSession(headers=HEADERS) as session:
        tasks = []
        for region_name, region_id in regions.items():
            for position in positions:
                for level in levels:
                    tasks.append(get_hh_vacancies_async(session, region_id, position, level))

        results = await asyncio.gather(*tasks)

        data = []
        index = 0
        for region_name in regions:
            for position in positions:
                for level in levels:
                    data.append({
                        "region": region_name,
                        "position": position,
                        "level": level,
                        "job_count": results[index] if results[index] is not None else 0
                    })
                    index += 1
        return data


# Streamlit UI
st.title("Вакансии с hh.ru")

# Кнопка для начала запроса
if st.button("Получить вакансии"):
    st.write("Загружаем данные...")

    # Асинхронный запуск функции
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    vacancies = loop.run_until_complete(get_all_vacancies())

    # Преобразование данных в DataFrame
    df = pd.DataFrame(vacancies)

    # Сохраняем данные в CSV
    df.to_csv('vacancies_data.csv', index=False)
    st.success("Данные сохранены в vacancies_data.csv")
    st.write(df)
    # Визуализация данных
    plt.figure(figsize=(10, 6))
    for position in df['position'].unique():
        subset = df[df['position'] == position]
        plt.bar(subset['region'] + ' - ' + subset['level'], subset['job_count'], label=position)

    plt.title('Количество вакансий по позициям и уровням')
    plt.xlabel('Регион - Уровень')
    plt.ylabel('Количество вакансий')
    plt.xticks(rotation=45)
    plt.legend()
    plt.tight_layout()

    # Отображаем график в Streamlit
    st.pyplot(plt)

