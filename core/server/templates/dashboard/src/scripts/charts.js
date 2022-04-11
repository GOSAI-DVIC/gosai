// When window is loaded

// let fps_chart_init = 0;

const fps_data = {
    datasets: [{
        label: 'fps',
        data: [],
        borderColor: 'rgb(255, 0, 0)',
        backgroundColor: 'rgb(255, 0, 0, 0.5)',
    }]
};

const fps_config = {
    type: 'line',
    data: fps_data,
    options: {
        color: '#ffffff',
        responsive: true,
        plugins: {
            legend: {
                position: 'top',
            },
            title: {
                color: '#ffffff',
                display: true,
                text: 'Realtime front FPS'
            }
        },
        scales: {
            y: {
                min: 0,
            }
        }
    },
};

const fps_ctx = document.getElementById('fps-display-chart').getContext('2d');
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

const ms_data = {
    datasets: []
}

const ms_config = {
    type: 'line',
    data: ms_data,
    options: {
        color: '#ffffff',
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                position: 'top',
            },
            title: {
                color: '#ffffff',
                display: true,
                text: 'Realtime front ms per application',
            }
        },
        scales: {
            y: {
                min: 0,
            }
        }
    },
};

const ms_ctx = document.getElementById('apps-looptime-chart').getContext('2d');
const ms_chart = new Chart(ms_ctx, ms_config);

let ms_colors = [
    "rgb(166,206,227)",
    "rgb(178,223,138)",
    "rgb(251,154,153)",
    "rgb(253,191,111)",
    "rgb(202,178,214)",
    "rgb(255,255,153)",
    "rgb(255,127,0)",
    "rgb(31,120,180)",
    "rgb(227,26,28)",
    "rgb(51,160,44)",
    "rgb(106,61,154)",
    "rgb(177,89,40)",
]

function update_ms_chart(new_entries) {
    let data = ms_chart.data;
    data.labels.push(new Date(new_entries.timestamp).getSeconds());
    for (const dataset of data.datasets) {
        let ms_time = new_entries.data[dataset.label];
        if (ms_time != undefined) dataset.data.push(mean(ms_time));
        else dataset.data.push(0);
    }

    for (const [name, ms_time] of Object.entries(new_entries.data)) {
        if (data.datasets.find(dataset => dataset.label == name) == undefined) {
            let len;
            if (data.datasets.length == 0) len = 0;
            else len = data.datasets[0].data.length - 1;
            data.datasets.push({
                label: name,
                data: new Array(len).fill(0),
                borderColor: ms_colors[data.datasets.length],
                backgroundColor: ms_colors[data.datasets.length],
            });
            let dataset = data.datasets[data.datasets.length - 1];
            dataset.data.push(mean(ms_time));
        }
    }
    ms_chart.update();
    for (const dataset of data.datasets) {
        if (dataset.data.length > 100) {
            dataset.data.shift();
        }
    }
    if (data.labels.length > 100) {
        data.labels.shift();
    }
    ms_chart.update();
}

function mean(array) {
    return array.reduce((a, b) => a + b) / array.length;
}

const drivers_lp_data = {
    datasets: []
}

const drivers_lp_config = {
    type: 'line',
    data: drivers_lp_data,
    options: {
        color: '#ffffff',
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                position: 'top',
            },
            title: {
                color: '#ffffff',
                display: true,
                text: 'Realtime drivers loop time',
            }
        },
        scales: {
            y: {
                min: 0,
            }
        }
    },
};


const drivers_lp_ctx = document.getElementById('drivers-looptime-chart').getContext('2d');
const drivers_lp_chart = new Chart(drivers_lp_ctx, drivers_lp_config);


function update_drivers_lp_chart(new_entries) {
    let data = drivers_lp_chart.data;
    data.labels.push(new Date(new_entries.timestamp).getSeconds());
    for (const dataset of data.datasets) {
        let driver_data = new_entries.data[dataset.label];
        if (driver_data != undefined && driver_data["loop_time"] != undefined) dataset.data.push(driver_data["loop_time"]);
        else dataset.data.push(0);
    }

    for (const [name, driver_data] of Object.entries(new_entries.data)) {
        if (driver_data["loop_time"] != undefined && data.datasets.find(dataset => dataset.label == name) == undefined) {
            let len;
            if (data.datasets.length == 0) len = 0;
            else len = data.datasets[0].data.length - 1;
            data.datasets.push({
                label: name,
                data: new Array(len).fill(0),
                borderColor: ms_colors[ms_colors.length - 1 - data.datasets.length],
                backgroundColor: ms_colors[ms_colors.length - 1 - data.datasets.length],
            });
            let dataset = data.datasets[data.datasets.length - 1];
            dataset.data.push(driver_data["loop_time"]);
        }
    }
    drivers_lp_chart.update();
    for (const dataset of data.datasets) {
        if (dataset.data.length > 100) {
            dataset.data.shift();
        }
    }
    if (data.labels.length > 100) {
        data.labels.shift();
    }
    drivers_lp_chart.update();
}
