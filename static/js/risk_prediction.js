// Monthly Prediction Trend
const predictionCtx = document.getElementById('predictionChart');

new Chart(predictionCtx, {
    type: 'bar',
    data: {
        labels: [
            'Jan','Feb','Mar','Apr','May','Jun',
            'Jul','Aug','Sep','Oct','Nov','Dec'
        ],
        datasets: [{
            label: 'High Risk Areas',
            data: [12,15,18,22,28,25,30,27,24,29,32,35],
            backgroundColor: '#f7933a',
            borderRadius: 5
        }]
    },
    options: {
        responsive:true,
        plugins:{
            legend:{
                display:false
            }
        }
    }
});


// Risk Distribution Pie Chart
const riskCtx = document.getElementById('riskChart');

new Chart(riskCtx,{
    type:'pie',
    data:{
        labels:[
            'High Risk 28%',
            'Low Risk 30%',
            'Medium Risk 42%'
        ],
        datasets:[{
            data:[28,30,42],
            backgroundColor:[
                '#ef4444',
                '#fbbf24',
                '#f7933a'
            ]
        }]
    },
    options:{
        responsive:true
    }
});

document.addEventListener("DOMContentLoaded", () => {
    const rows = document.querySelectorAll("tbody tr");

    rows.forEach(row => {
        row.addEventListener("mouseenter", () => {
            row.style.background = "#f9fafb";
        });

        row.addEventListener("mouseleave", () => {
            row.style.background = "transparent";
        });
    });
});
