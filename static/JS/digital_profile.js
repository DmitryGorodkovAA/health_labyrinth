
const ctx2 = document.getElementById('heartDiseaseChart').getContext('2d');
const heartDiseaseChart = new Chart(ctx2, {
    type: 'line',
    data: {
        labels: [15, 20, 25, 30, 35, 40, 45, 50, 55, 60],
        datasets: [{
            label: 'Вероятность сердечно-сосудистых заболеваний',
            font: 70,
            data: [10, 15, 20, 25, 30, 35, 40, 45, 50, 55],
            borderColor: '#004A3D',
            fill: false,
            font: {
                size: 20, // Размер шрифта
                family: 'Arial', // Шрифт (по желанию)
                weight: 'bold' // Жирность шрифта (по желанию)
            },
            color: '#015849' // Цвет шрифта метки
        }]
    },
    
    options: {
        scales: {
            y: {
                beginAtZero: true,
                title: {
                    display: true,
                    text: '%',
                    font: {
                        size: 13,  // Новый размер шрифта
                        weight: 'bold' // Жирный шрифт
                    },
                    color: '#004A3D' // Цвет текста
                },
                ticks: {
                    color: '#004A3D' // Цвет меток на оси Y
                }
            },
            x: {
                title: {
                    display: true,
                    text: 'Возраст',
                    font: {
                        size: 13,  // Новый размер шрифта
                        weight: 'bold' // Жирный шрифт
                    },
                    color: '#004A3D' // Цвет текста
                },
                ticks: {
                    color: '#004A3D' // Цвет меток на оси X
                }
            }
        }
    }
});



function updateCharts() {
    const age = document.getElementById('age').value;
    // Здесь можно обновить данные по выбранным параметрам
    // Например: scoliosisData = ..., cardioData = ...
    
    scoliosisChart.update();
    cardioChart.update();
}