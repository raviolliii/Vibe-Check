//=======================================================
// Constants and Utility Functions
//=======================================================

const $ = selector => document.querySelector(selector);
const $$ = selector => document.querySelectorAll(selector);
const round = d => Math.round(d * 1000) / 1000;
const COLORS = ['#ff6347', '#ffd700', '#65d26e', '#87ceeb', '#ffffff']


//=======================================================
// Chart.js config
//=======================================================

Chart.defaults.global.responsive = false;
Chart.defaults.global.animation.duration = 500;
Chart.defaults.global.hover.mode = 'nearest';
Chart.defaults.global.datasets.line = {
    showLine: true,
    fill: false,
    borderWidth: 2,
    pointRadius: 2,
    pointHitRadius: 8,
};
Chart.defaults.global.legend = {
    ...(Chart.defaults.global.legend),
    position: 'bottom',
    align: 'start',
};
Chart.defaults.global.legend.labels = {
    ...(Chart.defaults.global.legend.labels),
    boxWidth: 6,
    fontSize: 14,
    fontColor: '#bbbbbb',
    padding: 32,
    usePointStyle: true,
};
Chart.defaults.global.defaultFontSize = 14;
Chart.defaults.scale.gridLines = {
    ...(Chart.defaults.scale.gridLines),
    display: true, 
    color: 'transparent', 
    zeroLineColor: "#606060"
};
Chart.defaults.scale.scaleLabel = {
    ...(Chart.defaults.scale.scaleLabel),
    display: false,
    fontColor: "#bbbbbb",
};
Chart.defaults.scale.ticks.fontColor = '#606060';


//=======================================================
// Main/Rendering
//=======================================================

// fetch data from server, show chart with resulting data
const url = new URL(window.location.href);
fetch('/api' + url.pathname)
    .then(res => res.json())
    .then(showContent)
    .catch(console.error);

function showContent(data) {
    $('.artist-cover').setAttribute('src', data.imageURL)
    $('title').innerText = data.name;
    $('.artist-name').innerText = data.name;

    $('.loading-container').classList.add('hidden');
    $('.container').classList.remove('hidden');

    const datasets = data.albums.map((album, i) => {
        const points = album.songs.map((s, j) => ({
            label: s.name,
            x: j + 1,
            y: (((s.valence * 2) - 1) * 0.7) + (s.polarity) * 0.3,
            valence: (s.valence * 2) - 1,
            polarity: s.polarity
        }));
        const color = COLORS[i % COLORS.length];

        return {
            defaultColor: color,
            borderColor: color + '55', // line
            backgroundColor: color, // inside points/legends
            pointBorderColor: color, // points/legends ring
            label: album.name,
            data: points
        }
    });
    const labels = data.albums
        .map((a, i) => a.songs.map(s => s.name))
        .reduce((a, b) => a.concat(b), []);

    drawChart(labels, datasets);
}

function drawChart(labels, datasets) {
    const ctx = $('#canvas').getContext('2d');
 
    const graph = new Chart(ctx, {
        type: 'line',
        data: { labels, datasets },
        options: {
            legend: {
                onHover: (e, _) => e.target.style.cursor = 'pointer',
                onLeave: (e, _) => e.target.style.cursor = 'default',
            },
            scales: {
                xAxes: [{
                    type: 'linear',
                    scaleLabel: { labelString: 'Valence' },
                    ticks: {
                        display: false,
                        stepSize: 1,
                        suggestedMin: 0,
                        suggestedMax: Math.max(...datasets.map(d => d.data.length)) + 1,
                    },
                }],
                yAxes: [{
                    scaleLabel: { labelString: 'Polarity' },
                    ticks: {
                        padding: 10, 
                        min: -1.2, 
                        max: 1.2,
                        callback: (val, i, values) => {
                            return {
                                '-1': 'Dark',
                                '0': 'Neutral',
                                '1': 'Positive',
                            }[val] || '';
                        }
                    }
                }]
            },
            tooltips: {
                callbacks: {
                    title: function(items, data) {
                        const { datasetIndex, index } = items[0];
                        const dataset = data.datasets[datasetIndex];
                        let label = dataset.data[index].label || '';
                        return label;
                    },
                    label: function(item, data) {
                        const dataset = data.datasets[item.datasetIndex];
                        const { valence, polarity } = dataset.data[item.index];
                        const _valence = round(valence);
                        const _polarity = round(polarity);
                        return `(${_valence}, ${_polarity})`;
                    }
                }
            }
        }
    });
}

