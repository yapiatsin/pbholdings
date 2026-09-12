window.pbChartLegend = {
    display: true,
    position: 'bottom',
    fullSize: false,
    labels: {
        usePointStyle: true,
        boxWidth: 6,
        boxHeight: 6,
        font: { size: 10 },
        padding: 4,
        color: '#1a1a1a'
    }
};
window.pbChartLayout = { padding: { top: 4, right: 6, bottom: 0, left: 2 } };
window.pbDoughnutColors = [
    '37, 99, 235',
    '249, 115, 22',
    '234, 179, 8',
    '236, 72, 153',
    '16, 185, 129',
    '139, 92, 246'
];
window.pbBarScales = {
    x: {
        grid: { display: false },
        ticks: { color: '#888', font: { size: 10 }, maxRotation: 0 }
    },
    y: {
        beginAtZero: true,
        grid: { color: 'rgba(136, 136, 136, 0.18)' },
        ticks: { color: '#888', font: { size: 10 }, maxTicksLimit: 5 }
    }
};
window.pbLineHoverBand = {
    id: 'pbLineHoverBand',
    beforeDatasetsDraw: function (chart) {
        const actives = chart.getActiveElements();
        if (!actives.length) return;
        const area = chart.chartArea;
        const xScale = chart.scales.x;
        let x = actives[0].element.x;
        let width = 28;
        if (chart.config.type === 'bar' && xScale && typeof xScale.getPixelForValue === 'function') {
            const index = actives[0].index;
            x = xScale.getPixelForValue(index);
            const left = xScale.getPixelForValue(index - 0.5);
            const right = xScale.getPixelForValue(index + 0.5);
            if (isFinite(left) && isFinite(right)) {
                width = Math.max(28, Math.min(Math.abs(right - left) * 0.72, 64));
            }
        }
        const ctx = chart.ctx;
        ctx.save();
        ctx.fillStyle = (chart.options.plugins.pbLineHoverBand && chart.options.plugins.pbLineHoverBand.color) || 'rgba(168, 50, 50, 0.10)';
        ctx.fillRect(x - width / 2, area.top, width, area.bottom - area.top);
        ctx.restore();
    }
};
window.pbLineExternalTooltip = function (context) {
    let el = document.getElementById('pb-chart-tooltip');
    if (!el) {
        el = document.createElement('div');
        el.id = 'pb-chart-tooltip';
        el.className = 'pb-chart-tooltip';
        document.body.appendChild(el);
    }
    const tooltip = context.tooltip;
    if (!tooltip || tooltip.opacity === 0) {
        el.classList.remove('is-visible');
        return;
    }
    const title = (tooltip.title && tooltip.title[0]) ? tooltip.title[0] : '';
    const points = tooltip.dataPoints || [];
    let body = '';
    if (points.length > 1) {
        body = points.map(function (point) {
            const value = Number(point.raw || 0).toLocaleString('fr-FR');
            const label = point.dataset && point.dataset.label ? point.dataset.label : '';
            return '<div class="pb-chart-tooltip__row"><span class="pb-chart-tooltip__label">' + label + '</span><span class="pb-chart-tooltip__value">' + value + '</span></div>';
        }).join('');
    } else {
        const value = points[0] ? Number(points[0].raw || 0).toLocaleString('fr-FR') : '';
        body = '<div class="pb-chart-tooltip__value">' + value + '</div>';
    }
    el.innerHTML = '<div class="pb-chart-tooltip__date">' + title + '</div>' + body;
    const rect = context.chart.canvas.getBoundingClientRect();
    el.style.left = (rect.left + tooltip.caretX) + 'px';
    el.style.top = (rect.top + tooltip.caretY) + 'px';
    el.classList.add('is-visible');
};
window.pbResetChart = function (canvas) {
    if (!canvas || typeof Chart === 'undefined') return false;
    const existing = Chart.getChart(canvas);
    if (existing) existing.destroy();
    const tip = document.getElementById('pb-chart-tooltip');
    if (tip) tip.classList.remove('is-visible');
    return true;
};
window.pbMakeLineChart = function (canvas, labels, data, seriesLabel, rgb) {
    if (!window.pbResetChart(canvas)) return null;
    const ctx = canvas.getContext('2d');
    const height = (canvas.parentElement && canvas.parentElement.clientHeight) || 280;
    const fill = ctx.createLinearGradient(0, 0, 0, height);
    fill.addColorStop(0, 'rgba(' + rgb + ', 0.16)');
    fill.addColorStop(0.7, 'rgba(' + rgb + ', 0.04)');
    fill.addColorStop(1, 'rgba(' + rgb + ', 0)');
    return new Chart(ctx, {
        type: 'line',
        plugins: [window.pbLineHoverBand],
        data: {
            labels: labels,
            datasets: [{
                label: seriesLabel,
                data: data,
                borderColor: 'rgb(' + rgb + ')',
                backgroundColor: fill,
                borderWidth: 2.25,
                tension: 0.45,
                fill: true,
                pointRadius: 0,
                pointHoverRadius: 5,
                pointBackgroundColor: 'rgb(' + rgb + ')',
                pointHoverBackgroundColor: 'rgb(' + rgb + ')',
                pointBorderColor: '#fff',
                pointHoverBorderColor: '#fff',
                pointBorderWidth: 0,
                pointHoverBorderWidth: 2,
                pointHitRadius: 16
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            layout: { padding: { top: 8, right: 10, bottom: 0, left: 2 } },
            interaction: { mode: 'index', intersect: false },
            plugins: {
                pbLineHoverBand: { color: 'rgba(' + rgb + ', 0.10)' },
                legend: { display: false },
                tooltip: {
                    enabled: false,
                    external: window.pbLineExternalTooltip
                }
            },
            scales: {
                x: {
                    border: { display: false },
                    grid: { display: false },
                    ticks: { color: '#c4c4c4', font: { size: 10 }, maxRotation: 0 }
                },
                y: {
                    beginAtZero: true,
                    border: { display: false },
                    grid: { color: 'rgba(17, 24, 39, 0.06)' },
                    ticks: { color: '#c4c4c4', font: { size: 10 }, maxTicksLimit: 5 }
                }
            }
        }
    });
};
window.pbMakeBarChart = function (canvas, labels, series, extra) {
    if (!window.pbResetChart(canvas)) return null;
    extra = extra || {};
    const items = series || [];
    const bandRgb = (items[0] && items[0].rgb) || '168, 50, 50';
    const scales = {
        x: Object.assign({ stacked: !!extra.stacked }, window.pbBarScales.x),
        y: Object.assign({ stacked: !!extra.stacked }, window.pbBarScales.y)
    };
    return new Chart(canvas.getContext('2d'), {
        type: 'bar',
        plugins: [window.pbLineHoverBand],
        data: {
            labels: labels,
            datasets: items.map(function (item) {
                return {
                    label: item.label,
                    data: item.data,
                    borderWidth: 1,
                    borderColor: 'rgba(' + item.rgb + ', 0.9)',
                    backgroundColor: 'rgba(' + item.rgb + ', 0.16)',
                    hoverBackgroundColor: 'rgba(' + item.rgb + ', 0.38)',
                    hoverBorderColor: 'rgba(' + item.rgb + ', 1)',
                    borderRadius: 8,
                    borderSkipped: false,
                    maxBarThickness: extra.maxBarThickness || 16
                };
            })
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            layout: window.pbChartLayout,
            interaction: { mode: 'index', intersect: false },
            plugins: {
                pbLineHoverBand: { color: 'rgba(' + bandRgb + ', 0.10)' },
                legend: items.length > 1 ? window.pbChartLegend : { display: false },
                tooltip: {
                    enabled: false,
                    external: window.pbLineExternalTooltip
                }
            },
            scales: scales
        }
    });
};
window.pbMakeDoughnutChart = function (canvas, labels, data, colorList) {
    if (!window.pbResetChart(canvas)) return null;
    const colors = colorList && colorList.length ? colorList : window.pbDoughnutColors;
    return new Chart(canvas.getContext('2d'), {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: colors.map(function (color) { return 'rgba(' + color + ', 0.42)'; }),
                borderColor: '#fff',
                borderWidth: 2,
                hoverBackgroundColor: colors.map(function (color) { return 'rgba(' + color + ', 0.62)'; }),
                hoverBorderColor: '#fff'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: '58%',
            layout: { padding: { top: 4, right: 4, bottom: 4, left: 4 } },
            plugins: {
                legend: {
                    display: true,
                    position: 'right',
                    align: 'center',
                    fullSize: false,
                    labels: {
                        usePointStyle: true,
                        boxWidth: 6,
                        boxHeight: 6,
                        font: { size: 10 },
                        padding: 6,
                        color: '#1a1a1a'
                    }
                }
            }
        }
    });
};
