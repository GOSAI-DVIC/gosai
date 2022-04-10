// When window is loaded

// let fps_chart_init = 0;

const data = {
    datasets: [{
        label: 'fps',
        data: [],
        borderColor: 'rgb(255, 0, 0)',
        backgroundColor: 'rgb(255, 0, 0, 0.5)',
    }]
};

const fps_config = {
    type: 'line',
    data: data,
    options: {
        responsive: true,
        plugins: {
            legend: {
                position: 'top',
            },
            title: {
                display: true,
                text: 'Realtime FPS'
            }
        },
        scales: {
            y: {
                min: 0,
            }
        }
    },
};

const fps_ctx = document.getElementById('fps-performances-chart').getContext('2d');
const fps_chart = new Chart(fps_ctx, fps_config);

function update_fps_chart(new_entry) {
    let data = fps_chart.data;
    data.datasets[0].data.push(new_entry.y);
    data.labels.push(new Date(new_entry.x).getSeconds());

    fps_chart.update();
    if (data.datasets[0].data.length > 100) {
        data.labels.shift();
        data.datasets[0].data.shift();
    }
    fps_chart.update();
}
